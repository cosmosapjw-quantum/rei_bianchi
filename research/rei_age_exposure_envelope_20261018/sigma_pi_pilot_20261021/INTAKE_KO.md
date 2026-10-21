# 2026-10-21 fresh intake 범위와 재사용 결정

Intake 시작의 실제 PR199 HEAD는 964b2e3c098f6e475999a4eddc7a6aa0f8f053cc였고 publication 준비 직전 다시 읽었을 때도 같았다. PR은 open draft였다. 기존 v8 인계 HEAD를 현재 상태로 가정하지 않았다. 최신 CURRENT5와 v11 raw-diagnostic/review 및 추가 필수 v8 근거를 읽어 완료 campaign을 재사용했다.

## 실제 확인 범위

| Surface | 실제 확인 |
|---|---|
| REI GitHub |253 branch metadata,211 all-state PR metadata, pagination 끝 확인; 관련 PR source/result 상세 열람 |
| VigilODE GitHub |182 branch metadata,78 PR metadata,최근 workflow25, pagination 끝 확인 |
| 관련 repo |접근 가능한 owner repo51개 metadata 확인 후 BASS_HE,bass_cr,rec_bianchi,REI,VigilODE 관련 최신 PR 상세 확인 |
| Google Drive |지정 rei_bianchi_research_backups folder141개 direct entries; continuation 없음 |
| Dropbox age folder |38개 direct entries,has_more=false |
| Dropbox related REI folder |40개 entries,has_more=false |
| 다른 대화 |이번 personal-context search 실제 SUCCESS; 관련 최신 context 확보 |
| 새 작은 LRS backup |SSH handoff10863bytes와 exit followup46358bytes 실제 download/read |
| SciSpace/Exa |Einstein–Vlasov와 conservative momentum primary literature 검색, 핵심 primary PDF 식 열람 |
| Wolfram |Context tool internal error를 기록; 별도 evaluator에서 tensor traces/contractions 직접 계산 성공 |
| NCP 연결 |Device inventory SUCCESS; 실행 도구는 monthly usage cap으로 SSH 전에 차단 |

전체 branch/PR 목록 pagination은 완료했다. 모든 branch의 모든 file, 모든 과거 대화, 모든 cloud archive bytes를 읽었다는 주장은 하지 않는다. Dropbox 검색의 날짜 filter가 오래된 결과를 포함한 경우 직접 folder enumeration을 freshness 근거로 사용했다. 큰 기존 v11 archive와 모든 VigilODE full raw state를 다시 다운로드·검산하지 않았다.

## 유용한 결과와 적용

- REI PR147 3b85dedce84d37b3e165da00685a8a984950aafe: Einstein–kinetic LRS hierarchy/canonical Vlasov kernel와 prior finite-resolution outputs. 이번 pilot의 active source.
- REI PR145 54e29dff5a90c0a785cb6dcfb004403614ca403b: parent model/norm·equation provenance.
- Materialized source/results/license/PNG21개는 pinned Git blob SHA21/21 일치했다. Vendor kernel3개와 lock은 C9에서 다시 직접 byte equality 확인.
- PR141 80825585f9fe31d2ee0d5af545ada3fa1f52be72 / PR142 435c94308c0cd7b1ba8ff6518246da061f2fc2fa: 제한된 warm near-z4 native HHe–Einstein two-way 경로. Full cold-z20→4,UVQ4/recoil의 열린 조건이 있어 이번 source-free sweep의 결과로 합치지 않았다.
- PR210 e4c8133288614638792888367ca10b2ded3138ff / PR211 c9deb933761a8d2593d1176aee028cd423bdbc05: native T-table,prepared/rate-sharing·cubic acceleration. 현재 collisionless RHS에는 chemistry rate 호출이 없어 당일 plot을 위한 필수 변경이 아니다.
- PR198 3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8: 실제 SSH handoff와 LRS backlog144/246 complete,100 not-run,2 blocked. 새 Sigma–Pi pilot 완료물은 아니었다. 별도 LRS lane을 변경하거나 그100개를 현재 계약에 포함하지 않았다.
- VigilODE PR77 9bb05bed4cd7df720f2b429c2b47e97ed76712d5 / PR78 ebb5b81ebe77314b6fee941096fd6cba6d8597fc: 구조가 특정된 reflecting-band+rank-one solver evidence와 original archives. 현재 kinetic RHS의 generic drop-in solver로 인정하지 않았다.
- BASS_HE PR78 38493edccd9344c11fd66e63e1d938f77c2b093f / PR81 fcdf56d9a66b2d159d42a9a72131f94040cd5891: canary1/1과 reference4/4 reuse,READY empty.
- bass_cr PR89 dc1c0c0721b74454958e5d16264c24ec465ba1d8: NCP49 pending,new completed0.
- rec_bianchi PR110 888d56d72579d1e1fd30f66abe02d9f91809a767 / PR114 df95a074730ea0d13d609cf88d448f01f4a47ef1: U5 prior smoke HOLD와 U4 h/4 restart code/preflight; 새 NCP return 없음.

위 검사는 새 계산 전 중복을 피하고 재사용 가능한 source를 고르기 위한 것이다. 다른 repo의 scoped PASS를 이번 pilot의 scientific validation으로 대체하지 않았다.

## 작은 backup 실체

- SSH handoff:10863bytes,SHA256 f2f9223e20812eb2d4d0dbea0a24d8af22002e681e7fa5738ba58b2d712b4818.
- Exit followup:46358bytes,SHA256 baf26a79d2e3c07376de6d338b780c0ab2082a36c6b805e340b01a5ddb02eeeb.
- 기존 C15v2/SigmaPi response archive와 RUN19/HE29 closeout은 관련 source/history로 식별했다. 확인 범위에서 이번 새91점의 완료 결과는 없었다.

계정 전체 repo 목록, raw conversation context, temporary signed download URLs는 공개 연구 package에 포함하지 않는다. Source selection·계산에 필요한 최소 provenance만 게시한다. Owner checkout은 접근 가능한 NCP 실행 도구가 cap으로 막혀 이번 세션 직접 재관측하지 못했고, 어떤 owner file/process/branch도 변경하지 않았다.

