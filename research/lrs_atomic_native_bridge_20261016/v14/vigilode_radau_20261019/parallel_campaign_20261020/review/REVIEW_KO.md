# 독립 C9/R6 검토 — 자원 제한 병렬 이력 실행

## 판정

**PASS_SCOPED_RESOURCE_AWARE_ORCHESTRATION. 현재 blocking finding은 0개다.**

구현하지 않은 독립 Astra reviewer가 동결된 12개 파일, 원본·derived example, 실제 compile와 raw, 21개 표적 process 시험, 이력 독립성과 실행시간 유도를 한 검토 episode에서 읽었다. 복원 의존성의 resume 연결 오류와 V12 reference 경로는 같은 episode에서 수정·확인했다. 추가 native 실행이나 새 검토 gate는 필요하지 않다.

이 판정은 **구현된 실행 경로와 이번 유한 로컬 검증**을 승인한다. 전체 V12/V13/SSPRK2 backlog의 새 NCP 실행은 아직 NOT_RUN이며 root가 관측한 실행 도구 quota0·지정 SSH key 부재가 남아 있다. 기존 source524 NCP19, borrowed N2, 원본 V14 NCP84의 완료 상태는 유지한다.

## 동결된 구현과 과학 범위

- Base metadata HEAD: `96aaad584bbecded34485526a4bb53a49708ffc6`.
- 현재 Radau scientific source: `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`.
- VigilODE pin: `8a8bd409b1d96c7b7421f496d229e119fd3d284e`.
- 실제 비교 binary: `c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992`.
- 최종 12파일 manifest SHA256: `dd686ea1eee2437dea754d771098ee9b87a93b53780d99f3de6a18813c13a7a9`.
- delivery diff: 121,880 bytes, SHA256 `b6a372f4f4df4be05194998709d23c0282a84acb85411707e9e255c39646894c`.

모든 최종 파일의 크기·SHA256이 manifest와 일치했다. 기존 파일 변경은 `prepare_and_run.py`의 build jobs·build-only·명시적 focused-tests 옵션, target 환경 정리와 receipt 필드다. 나머지는 새 parallel campaign 디렉터리다. 이번 diff는 원본 native 수식·기존 append hook·VigilODE source·Cargo pin/lock·허용오차·provider/EOS/FD/GL2 birth·default/transaction을 바꾸지 않는다. 이전의 유효한 source closure를 재사용했고 전체637파일 감사를 반복하지 않았다.

V12 144이력, V13 84이력, SSPRK2 transport52행·coupled16이력을 원모델 그대로 NCP 호스트에서 재현하는 준비다. Native command231개와 준비·시험·병합·분석을 합쳐246 jobs다. V12/V13의228개 이력은 각각 독립 작업으로 배치한다. **새 과학 모델 수는0**이며 최신 cell-cache의 seeded-disabled를 V12 photon-free나 V13 solver에 대입하지 않는다.

## R6: 이력 독립성과 비용식

원본 example은 매 이력마다 driver, state, local clock과 누적 ledger를 초기화한다. 각 이력의 결정적 수치 연산은 서로 다른 데이터 블록에만 작용하므로 순서를 바꾸어도 각 이력의 결과가 같다. 시간 의존 연속계의 flow 표현에서는 각 이력에 자체 시간좌표 τ_j를 붙이면 서로 다른 (τ_j,y_j) 블록의 vector field가 교환한다. 이는 서로 다른 이력 사이의 진술이며, 한 LRS 상태 안의 operator splitting이나 전역 Jacobian 구조·global certificate의 승인이 아니다.

total-H의 Y=.2454/[4(1−.2454)]=1227/15092, e=x+Y(y+2z), de/dt=dx/dt+Y(dy/dt+2dz/dt)를 독립 대수로 확인했다. V12 CSV의 helium per_H 열에는 이미Y가 들어 있으므로 e=HII_per_H+HeII_per_H+2HeIII_per_H라는 새 진단식도 같은 정규화다.

고정된 양의 작업시간, p개의 동일 worker, 동시에 ready인 독립 작업과 work-conserving list scheduling이라는 이상화 아래 W=Σt_j, L=max t_j이면

\[
\max(W/p,L)\le T_p\le W/p+(1-1/p)L.
\]

마지막 완료 작업의 시작을 s, 시간을 t_j라 하면 시작 전 worker가 모두 바빴으므로 ps≤W−t_j이고 상한을 얻는다. 실제 restore/build/merge·메모리 대기·polling 비용은 이 이상적 모델의 가정 밖이다.

공통 setup/build B를 양쪽에 넣은 S=(B+W)/(B+T_p)의 미분은 (T_p−W)/(B+T_p)²이며 T_p<W일 때 감소한다. 실제 Cargo 병렬 build 가속은 측정하지 않았다. 다른 경계의 NCP compile wall과 raw 내부시간을 나눈 가속률도 만들지 않았다. 실제 Wolfram 두 반환에서 식·부호·block bracket을 확인했고 첫 반환의 undefined-symbol 경고는 보존했다.

## 실제 raw와 시험의 독립 확인

### 원본 대비 대표 shard

원본 SHA를 확인하고 selector 삽입을 제거했을 때 원문 전체 bytes가 정확히 복원됐다. 게시할 derived source도 실제 compile/run에 사용한 파일과 같았다. V13 while guard는 N을 증가시킨 후 skip하며 필수 selector는 CSV 생성 전에 검사한다.

| 실제 shard | 행 | 유한 숫자 비교 | 기타 비교 | 차이 |
|---|---:|---:|---:|---:|
| V12 D1_X1E5 / owner_like_be / N8 / cells8 | 8 | 344 | 16 | 0 |
| V13 X1e-4 / be_control / N8 / cells32 / tol1e-15 | 8 | 232 | 8 | 0 |

기존 saved raw와 실제 새 raw를 직접 읽고 header·step·모든 비시간 열을 비교했다. 제외한 열은 V12 elapsed_wall_s와 V13 wall_s뿐이다. dt_s와 물리·진단 수치는 포함했다. finite Decimal 비교와 문자열 일치이며 signed-zero bitwise 검증 주장은 아니다.

V12 release build는 exit0였다. V13의 초기 공유 target compile은 exit101이었고, 같은 원본 source를 variant 전용 target에서 빌드한 실행은 exit0였다. 실제 명령·stderr·실패와 수정 성공 기록을 읽었다. 최종 recipe는 target을 variant별로 분리한다.

### 기존 current binary의 직렬·병렬 비교

18개 실제 native 실행의 argv·binary binding·exit·raw·stdout/stderr hash를 직접 확인했다. 모두 CellCache, profile-off, RadauN16, completed=true·exit0다. fixed/birth/disabled RHS는 각각2992/8666/8871로 유지됐다.

9개 paired 비교에서 root wall_s만 제외하고 **유한 숫자463,323개, 기타72개, container35,619개가 일치**했다. 직렬은CPU0, 병렬은 서로 겹치지 않는CPU0/1/2를 사용했다.

| Pair 순서 | Serial phase s | Parallel phase s | 비율 |
|---|---:|---:|---:|
| AB | 1.656947672 | 0.753377051 | 2.199360426 |
| BA | 1.618014477 | 0.702647920 | 2.302738585 |
| AB | 1.666196855 | 0.775281123 | 2.149151844 |

중앙값 **2.199360426**은 이 로컬 호스트의 세 이력을 처리한3-worker 관측으로 채택한다. 시간은 input hash와 receipt를 포함한 동일한 campaign.run 외부 phase 경계다. NCP64 scaling, compiler·개별 RHS 가속, peak RSS 또는 이전 borrowed 속도·메모리 입증 상태로 확장하지 않는다.

별도 profile-on3회도 actual inputs/outcome/exit/stderr/raw hash와 일치했다. 이 profile은 비용 선택 근거이며 위 가속률 계산에 사용하지 않았다. inclusive Jacobian 시간은 exclusive timer 합에 중복 합산하지 않았다.

### 최종 변경의 표적 검증

새17개와 기존 runner4개, **총21개 process tests가 실제 PASS**한 stderr·exit와 log hash를 확인했다. fake child·restore/compile stub은 orchestration과 flag routing 검사이며 native 물리 시험으로 세지 않았다. 실제 native build/raw는 위의 별도 근거다.

수정 전 이미 완료된2개 shard와18개 paired native 실행은 유지한다. 최종 수정은 restore binding·resume dependent 상태·reference 경로와 분석 진단에 한정되고 native binary·수식·selector와 실제 과학 argv가 유지된다. 수정한 경로에 해당하는 표적 process 회귀를 연결했으며 native를 다시 실행하지 않았다.

## 닫힌 지적과 실행 인계

1. **복원 입력 identity 누락:** V13 restore/script/spec/chunks, V14 script/spec/payload, SSPRK restore/spec/native payload를 실제로 바인딩했다. parent identity mismatch가 남은 과거 completed dependent도 현재 DAG에서 BLOCKED로 표시하며 결과 bytes를 보존한다. 관련 두 표적 시험이 PASS했다.
2. **V12 reference 경로:** evidence/analysis/NATIVE_ANALYSIS.json을 놓치던 단일 glob을 recursive 탐색으로 고쳤다. 기존 reference가 있는데 absent로 표시하는 오류를 닫았다.
3. **초기 V13 target 충돌:** 최초 실패를 보존한 채 전용 target compile 성공으로 닫았다. 수치 source나 허용오차를 바꾸지 않았다.

Memory planner는 raw remaining과 관측 inactive_file의 회수 가능 추정을 분리하고20% 여유를 둔다. nominal reservation은 측정 RSS가 아니며 actual RSS 감소 주장은 없다. CSV merge는 정확한 key·step·header와 원래 순서를 검사한다. SSPRK alias는 원본 bytes를 보존하며 old audit의 과거 reviewer 문자열과 이번 독립 검토를 구분한다.

이번 실제 로컬 native 호출은 profile3+shard2+scheduler18=23회, 새 unique 모델0이다. 전체 backlog의 NCP 실행과 V13/SSPRK full-backlog 분석은 아직 남아 있다. 기존 source-on 일반2차, uniform stiff, 일반 양수성, CaseB/fullEoR/signedBianchi, 넓은 positive-CMB·비영 boundary, continuous global certificate와 해당 CSV가 제공하지 않는 완전 photon ledger는 HOLD다. production은 NOT_ISSUED다.

Root는 이 동결된 구현과 검토를 채택·게시하고 백업을 보존할 수 있다. 인증된 NCP 실행 수단이 실제로 제공되면 README의 유한 backlog 명령으로 이어간다. 이 reviewer는 Git/provider를 변경하거나 게시 ACK를 발행하지 않았다.

## 사용한 정책과 검토 방법

physmath-research-loop1.3.0의 SKILL, POLICY_INTEGRATION, CODING_LOOP, SUBAGENT_MODE, THEORY_LOOP를 실제 읽고 적용했다. read-only R2/C2 intake와 한 R6/C9 episode이며 하위 reviewer를 만들지 않았다. 불변 source의 BYTE_IDENTITY와 scientific output의 NUMERICAL/CONTENT_IDENTITY를 구별하고, 결과·provenance·포장 validity를 분리했다. 이전1.0.0 context와 기존 source/과학 계약은 역사적으로 보존했다. 정확한 source·evidence hash와18개 직접 raw 확인 기록은 INDEPENDENT_REVIEW.json에 있다.

