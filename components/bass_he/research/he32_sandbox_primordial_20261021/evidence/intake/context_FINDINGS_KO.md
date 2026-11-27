# HE32 최신 백업·대화·첨부 조사

조사 종료: 2026-10-21 14:45:42 UTC / 23:45:42 KST. 델타 기준은 HE31의 실제 마지막 context scan인 13:11 UTC다. 최종 게시 시각인 13:53 UTC를 쓰면 그 사이 다른 연구에서 완성한 결과가 누락되므로 scan 기준을 채택했다.

## 직접 확인한 새 결과

| 연구 | 이번 실제 읽기 | 확인한 결과와 현재 적용 |
|---|---|---|
| REI D9 / PR199 | 최종 4,576,719 B archive 전체 GET 및 hash; 원 결과·유도·코드·판정 선별 읽기; 후속 ACK 직접 fetch | 기존 175개 z20→2/153epoch 이력의 integrating-factor 성분 응력 budget. new IVP0. source `407f2a30efcdd0c4c4afb180cbe7d31f90cc0401`, metadata `cce008b3fc32c298185b30550b2cd909d74fcd87`. 새 full-species donor가 아니다. |
| BASS/REI ACCEL03 / PR179·217 | 최종 7,286,437 B archive 전체 GET/hash; 보고서·aggregate 요약 읽기 | warm729와 기존 NCP5의 이식 가능한 분석, NCP5 수치동등성 scoped 수용. new IVP/build0. REI source `39ae7c843ea2d1adf580aff44aebfdedea7e33aa`. |
| bass_cr C21N / PR94·95 | NCP-return closeout 442,823 B 전체 GET/hash; 원 NCP4 summary·scope review·README 읽기 | 새 물리 입력 4개를 sandbox/NCP 양쪽에서 실행. 40state, z20→4, case당101samples. 이전125와 합쳐 고유129. 두 사이트를8새입력으로 세지 않는다. Full reionization은 원 판정 HOLD. |
| WU088_HH PHYS77 / PR132 | post-publication delivery JSON 실제 fetch | 저장 유한 계수 owner IVP의 첫 셀 z20→19.534353 enclosure; new ODE0. final `d43cf2df2c4864ae05049f44301c5b389b80a49c`. 원 full-history 의무 유지. |
| 원자·핵 RUN19 / PR211 | Drive FINAL_HANDOFF 원문 fetch | HHeD exact-T sharing,32769-node cubic rate cache,Li number-source compatibility,VF1996BeRR3채널,19반응 target manifest가 준비됨. science `e540256ecf77df1c88fccb57b81d5d60110f367c`. NativeIVP0; full19/LiBe/nuclear/fullEoR 의무는 원문에서도 열려 있음. |

세 archive는 실제 성공한 full GET bytes, SHA256, Dropbox block hash가 모두 일치했다. 기본 sandbox 네트워크 차단을 만났고 승인된 read-only escalation으로 취득했다. 원 archive 안의 script/binary를 실행하지 않았다. 새 물리 적분·과거 결과 재실행·benchmark는 모두0이다. 상세 bytes/ID/hash는 `DOWNLOAD_READBACK.json`, 수치·scope는 `NEW_RESULTS_SYNTHESIS.json`에 있다.

## 이번 최종 연구에서 재사용할 연결

D9는
\[
M=(a/a_i)^3H/H_i,\quad S_F=\sqrt6s/H,\quad
M S_F=S_{F,i}+\int M P_m\,d\ln a+\int M P_r\,d\ln a
\]
를 실제 저장 이력에서 확인했다. 최대 scale-normalized residual `1.473444875767401e-6`, 원 기준 `2e-5`, 175/175통과다. 초기 \(S_F=.003,P_r=-.001\)의 다섯 matter 조건 중 네 부호전환을 설명하는 진단이며, 이번 새 chemically coupled trajectory에도 동일한 shear-equation convention이면 비교 가능한 source-budget 진단을 만들 수 있다. 이전 raw를 새 chemistry 결과로 표기하지 않는다.

RUN19의 재사용 후보 경로는 `research/atomic_nuclear_ssot_20261017/run19/metals/network/TARGET_NETWORK_19.json`과 `RESUME_KO.md`, `UNIT_B_FINAL_KO.md`다. 최종 archive는 `REI_RUN19_FINAL_T_RATE_ACCELERATION_LI_BE_20261020.zip`,25,344,988 B,SHA256 `6421ead745f3e5d298286e13b9515b7f668dcbb72de11b9f86650021c92b4f62`,Dropbox ID `id:BSpOijBcT10AAAAAAD_SVw`다. 이번 조사에서는 handoff 원문을 실제 읽었으며 이 25MB archive까지 재다운로드했다고 주장하지 않는다. GitHub 소스 조사 담당자에게 전달했다.

## 조회 범위

| 서비스 | 실제 범위 | 완료 상태 |
|---|---|---|
| Dropbox HE dossier | 하위폴더까지 recursive8pages,4,692entries | 마지막 has_more=false |
| Dropbox REI backups | recursive1page,74entries | has_more=false |
| Dropbox BASS_BACKUPS | recursive1page,223entries | has_more=false |
| Drive HE dossier | direct children1,000items | API상한으로 부분 목록 |
| Drive HE document MIME 검색 | provider pagination3pages,926items | token 소진; ZIP/gzip 전체 포함으로 확대하지 않음 |
| Drive REI backup folder | direct156items | 반환 범위 확인, pagination field없는 목록 |
| Personal Context | 실제1회 호출 | `Personal context is unavailable for this conversation.`; 취득 대화0 |

Drive 시간필터 검색은0개를 반환했지만 direct 목록에는 새 D9와 HE31파일이 있었다. 따라서 검색0을 파일 부재의 근거로 쓰지 않았다. Drive direct top_k10000 시도는 API 최대1000으로HTTP400을 반환했다. 자료상 완전성 범위를 정확히 위 표에 남긴다. 다른 대화의 사용자 제공 메모리 문맥과 실제 대화 검색 성공 여부를 구분한다.

## 첨부 그림

처음 사용자 메시지의 경로 부재 오류 뒤 파일이 도착했고 실제 시각 판독했다. 파일1,856,861 B,SHA256 `472ba6be633d2b5fc05fc1e0e88f965ff3c0311b0697e3c35c05bbca1629e6f9`.

그림은 n,H1,D,T,3He,4He,7Li 및19반응을 나타낸다. 원자이온화/재결합3종, 광핵6종, beta2종, 핵포획·핵반응8종으로 목록을 읽을 수 있다. 그림의 Li는 I/II/III까지만 있어 완전박리 LiIV와6Li는 그림의 표시범위 밖이다. 사용자 확대요청의 종목록을 별도로 명시해야 한다. 그림은 물리 반응률·초기 abundance·UV/MeV photon source를 제공하지 않으므로 이 값은 검증된 code/literature/input에서 채택해야 한다. 기존20첨부 archive의 member목록은 이전 조사파일을 재사용했고 전체 재추출·재해시는 하지 않았다.

## 보존·인계

`COVERAGE.json`, `NEW_RESULTS_SYNTHESIS.json`, `DOWNLOAD_READBACK.json` 및 본 문서는 공개 연구 provenance로 전달 가능하다. `downloads_private.json`은 일회용 download URL을 포함하는 조사 임시파일이므로 Git/백업 deliverable에 포함하지 않는다. 원격 계정 metadata와 취득 source 전체는 조사 디렉터리에만 보존했다.

이번 조회에서 새 native full-z20→2 H/He/Li 전구간 donor는 확인되지 않았다. 이는 위 실제 조회·읽기 범위의 결과다. 기존 최근 원자/핵 lane은 준비된 반응률/종 bookkeeping을 제공하므로 source identity를 확인해 최종 새 구현에 적극 재사용할 수 있다.
