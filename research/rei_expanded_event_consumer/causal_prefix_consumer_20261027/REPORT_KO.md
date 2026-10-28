# REI causal-prefix consumer 연구 결과

## 판정

이론 R1–R10의 구성적 정리와 코딩 C1–C10의 단회 실행·저장 결과 검토를 수행했다. 수치 범위는 PASS_SAVED_RESULTS_WITHIN_INFORMATION_POLYTOPE_AND_INTERFACE_SCOPE다. 자원 및 전체 admission은 HOLD_RESOURCE_NO_GLOBAL_OR_L4_PROMOTION이다. 실행은1회, 재실행0회이며3,189/3,189검사가 통과했다. 실제 CPU가 예약과 누적 한도를 넘어 새 local planning·과학 실행을 중단했다.

원래 DAG는 작업32/88·중앙27/88, 원노드 추가완료0이다. REC-COUPLED의 기존 constructive partial 상태, L4_ready=false 및 global_physical_completion=null을 유지한다. 현재 연구 루프의20단계와 원래88노드 집계를 서로 바꾸어 세지 않는다. 단계별 실제 게시·Drive/Dropbox 영수증은 delivery/STAGE_BACKUP_RECEIPTS.json에 모은다.

## 실제 새 근거와 연구 결과

7repo의1,387branch metadata를 페이지 끝까지 조사하고, 각repo 최근50PR metadata가 이전cutoff를 지나는지 확인했다. 지정Dropbox256개·Drive252개·최근Library6개와 대화 검색의 연구 관련 lead를 대조했다. 모든 branch본문이나 모든 private대화 전체를 읽었다는 뜻은 아니다. 새 유효 입력은 CR PR108의 finite-age pulse 누적량이다. 최종 bounded refresh2026-10-27 18:57:55–19:00:38 KST에서 원문4개와 CR head2776752d가 동일했다. WU는dde0806d로 진행했지만 실제physical_consumer/energy_Q는null인분자모델 prototype이라 기존selectedevent를 유지했다.

두 finest case chi1.5_R80_N2048·chi3_R80_N2048, 각각source-z2.316/2.479/2.649를 별도대안으로 소비했다. 실제7horizon,36canonicalbin,126연속sourcewindow,252scalarN/Ewindow를 사용한다. Source의원문UTF8과2^53초과정수를그대로보존했다. 기존PR219 bootstrap·83·GRID044·PR221조건부및PR233/235/236/237/239를재사용했다. GRID044는cosmologicalhistory식별자이며44점photonenergygrid가아니다.

핵심은 같은pulse의F_i를공통변수로 유지하는 것이다. l_i=max(0,L_0,…,L_i),u_i=min(P_U,U_i,…,U_m)라두면P비공집합조건은모든l_i≤u_i이며,

max(0,l_b−u_a) ≤ F_b−F_a ≤ u_b−l_a.

THEORY_KO.md에양끝을달성하는전체단조경로와두endpointpolygon의정확한확장증명을두었다. 이sharpness는저장된interval·monotonicity정보집합안의결론이다. fixed-K동역학집합전체,continuum모델오차 또는 실제우주론시간이력에대한sharpness가아니다.

0→10^7properseconds전체window에서기존각bin의marginalinterval폭을합한값과공통prefix폭의비는다음과같다. 아래는저장된유리수결과의표시용반올림이며새수치검사가아니다.

| χ | source-z | count 폭비 | kinetic-energy 폭비 |
|---:|---:|---:|---:|
| 1.5 | 2.316 | 23065.1 | 18503.9 |
| 1.5 | 2.479 | 23080.8 | 18491.9 |
| 1.5 | 2.649 | 23098.0 | 18480.5 |
| 3 | 2.316 | 19823.4 | 18028.7 |
| 3 | 2.479 | 19825.6 | 18020.8 |
| 3 | 2.649 | 19828.7 | 18013.2 |

예를들어χ1.5,z2.316의count최종구간은[4.836251649517417e−18,4.836332659440835e−18]cm^-3다. 공유prefix폭8.100992341772491e−23에비해독립bin폭합은1.8684987396545225e−18이다. 이는같은내부경계의불확실성을중복해서선택하지않은정보표현의개선이며물리불확실성전체가2만배감소했다는뜻이아니다.

## 정규화·시간좌표·단일소유권

raw N[cm^-3],E[eVcm^-3]를n=10^6N,e=10^6eV_J E로한번만변환한다. 명시적b>0에서native25의ΔY11=n/b,ΔY12=−n/b,Δzeta=−n/b,Δw_nt=−e/b이며나머지행은0이다. 별도retainedphoton에(n/b,(e+In)/b)를두고binding변화는−In/b다. 같은N/Epair에서전하·열입자수·에너지합이정확히보존된다. 외부injection에너지를capture의w_ext로다시계상하지않는다.

b미제공은propervolume값과null nativeprojection을남긴다. b=1.4e6m^-3는consumerfixture이며actualrecipientnb가아니다. 변하는기준밀도는

s(F_b/b_b−F_a/b_a)=s(F_b−F_a)/b_b+sF_a(1/b_b−1/b_a)

로분해하고양쪽b의몫미분을모두포함했다. 양의F_a를가진a=1,b=6검사를사용해보정항이나db_a누락이0입력으로숨지않도록했다. Endpoint차이를미공급∫j(t)/b(t)dt로대체하지않았다. 기존continuous reference식dotr+3Hr=R_r,F_x=(S−xR_r)/r도유지한다.

Integratedevent는clock불변이다. suppliedΔeta가있을때만bin평균을ΔT/Δeta로변환한다. manufacturedeta의nonzero dΔT=.17ΔT와dΔeta=−.09Δeta는별도인자다. C5에서한인자를공유하던wrapper결함을한번수리했고독립검토와실제검사가이를확인했다. max/min선택점의일반smoothJacobian,unknownsourcehorizon미분은주장하지않는다.

## 실제 검증과 독립 검토

단일명령은 python -B implementation/run_bounded.py였다. C5code commit은cfc2115fa868595f6adcf45fe7083f95ee637b90, 실행manifestSHA256는b6063f4b6e9fc31b22fd3753a076e367ff17dd0d4bf1e973ba9bc629ba2f54d5다. 원시결과commit은4a82442ce5476ac10a6417f209fc74f1ff7c43ab다.

- 3,189개검사전부PASS; exit0,stderr0bytes.
- 실제252scalarwindow,126sourcewindow,36canonicalbin과6source의identity·상관사상검사.
- 정확한rational경계·attainingwitness·독립inequality/corneroracle·outwardfloatcontainment.
- 264interface derivative저장값과528FD저장결과. 두step2e−4·1e−4의최대저장상대잔차2.7094758927889796e−10,기준2e−8.
- 양의prefix·누락reference/db_a·잘못된endpointclock·중복event·독립reservoircorner·invalidnormalization/timewidth 등의판별대조.
- Wolfram단회기호검산5항등식잔차0. SciSpace·Exa원전조사는SOURCE_REUSE_KO.md의확인수준으로기록했다.

Astra역할의root가문제·계약·판정을소유하고lower-tier요청executor가코드를작성·실행했다. 실제내부runtime모델identity는미확인으로기록했다. 다른Astra검토자는코드작성없이R6/C5및게시된raw결과의C9를검토했다. 원자료·검증·전제의byteidentity를필요범위로사용했고새수치재현을반복하지않았다.

## 자원 결과와 중단선

| 항목 | 실제CPU초 | 동결목표CPU초 |
|---|---:|---:|
| child |0.192151|0.12|
| wrapper |0.074169|0.04|
| heldreceipt tail |0.020000|0.02|
| 합계 |0.286320|0.18|

wall0.216493492s,RSS16840KiB였다. 실행예약초과0.106320s를그대로청구했다. Planning의기존누적14.791170885에더한15.077490885는임시14.99보다0.087490885크다. within_targets=false이며resourcegate는HOLD다. 수치검사PASS로이초과를지우지않았다. 사후한도인상·초기화·다른owner예산이체·재실행은없다. Main595.225063/600,NO_MORE_IVPs를유지한다.

AGENTS의원래planning10/presentation30에서50%미만임시인상규칙상새로운planning≥15의승인은별도다. 이번단위종료시원래policycap10/30으로복원하고초과누적을보존한다. 최종presentation실측·예약은BUDGET_STATUS.json와최종deliveryreceipt를참조한다. Remote/tool/LLM및미측정tail은UNKNOWN_NOT_ZERO다. 이후작업은저장결과해석·게시·복구용패키징이며새과학계산을presentation으로이체하지않았다.

## 남은 실제 연구 의무

CR공개finalC9는여전히PENDING이다. 실제sourcehistory·recipientnb·source-matchedphotonmeasure,RECfiniteopacity,BASStransport/absorption/errorradius,HEphysicalstopping/thermalization및미분,REInativeVigilODEclient/tube가필요하다. 공급자의generic성공을이연결의성공으로승격하지않는다. 전체망/L4완료는별도gate다. 다음스레드는새게시결과의변경된의존성부터이어가고이번attempt01과기존83·NCP·IVP·projection·quadrature·fullsuite를자동재실행하지않는다.

## 최종 전달 기록 — 2026-10-27 19:26:03 KST

소스 snapshot은31d088bb0923d29147efa0d1b358c546fc7f68d3이며77payload파일과1개archiveauthority를포함한ZIP525104bytes다. SHA256는70fcb00fab1b5e45904179acc07a8157cb72c3c6b6d20942f05d7b798ad3712d이다. 별도metadata ZIP37577bytes도양쪽backup에서완료됐다. Source77파일의Gitblob·size가모두일치했다.

원래policycap10/30으로복원했고planning15.077490885,presentation실측·기존예약43.528719494+finaltail.05=43.578719494를유지했다. 이번단위는CLOSED_DELIVERY_WITH_RESOURCE_HOLD다. 최종실제HEAD와ACK는PR240및delivery/FINAL_DELIVERY_RECEIPT.json을참조한다.
