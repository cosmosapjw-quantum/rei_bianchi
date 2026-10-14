# PHYS26 단일 후속 handoff — 평균·분산 고정 HeIII 응답의 정확한 구간

과제 후보: PHYS26_MEAN18_FIXED_VARIANCE_RESPONSE_ENVELOPE  \
선행 연구: REI-PHYS25-20261011 · PHYS25 완료 판정과 게시 receipt를 함께 소비한다.  \
상태: **이 문서는 다음 연구의 계약 후보이며 PHYS26을 실행한 결과가 아니다.**

## 1. 다음 한 문장 질문

**평균 18 eV와 광자 에너지 분산 \(W\)를 모두 고정했을 때 가능한 HeIII 초기 \(\epsilon^2t^4\) 응답 \(A\)의 정확한 전체 구간은 무엇이며, 어떤 분산에서는 모든 스펙트럼의 부호가 강제되는가?**

PHYS25는 처음 비음수 응답이 가능해지는 최소 분산 \(V_*\)와 유일한 최적 두 선을 닫았다. 또한 \(V_*\) 바로 위에는 같은 평균·분산으로 양·음 응답이 모두 가능한 작은 구간이 있음을 증명했다. 다음 단계는 이 구간과 그 양쪽 경계를 전체 허용 분산에서 정량적으로 닫는 것이다. 다른 평균·다른 초기 기체·유한 시간 계산으로 확장하지 않는다.

## 2. 다음 시작 시 실제로 확보할 입력

저장소는 cosmosapjw-quantum/rei_bianchi, branch는 forward/rust-reion-kernels-20260922, draft PR은 83이다. PHYS25의 입력 head는 a4ef8e95ce2a13388a85b79d072eba4344ab8a46이고 과학 소스 트리는 cb69b4736dd046e4675557577eb8e0ead037d1f3다.

PHYS25의 새 게시 커밋은 이 handoff 동결 이후 만들어지므로 여기에서 해시를 예측하지 않는다. 다음 시작 시 실제 최신 head와 PHYS25_PUBLICATION_RECEIPT.json을 읽어 게시 커밋·트리·추가 문서 경로를 확인한다. 게시 경로는 docs/fastest_track_chat/REI-PHYS25-20261011/다. 과학 소스가 달라졌으면 최신 이름만 보고 기존 수학 입력을 자동 승계하지 말고 차이가 관련 있는지 먼저 판단한다.

필수 닫힌 입력은 다음과 같다.

- PHYS25_PHYSICS_CONTRACT에 해당하는 PHYSICS_CONTRACT.json과 SOURCE_MANIFEST.json.
- report/PHYS25_REPORT_KO.md 및 PHYS25_RESULTS_SUMMARY.json.
- independent/DECISION_REVIEW.json과 DECISION_REVIEW_KO.md; 실제 판정 범위와 NONBLIND 역할 독립성을 유지한다.
- contributions/variational/VARIANCE_MINIMUM_DERIVATION_KO.md.
- contributions/derivative/THIRD_DERIVATIVE_CERTIFICATE.json 및 유도문.
- contributions/numerics/VARIANCE_CANDIDATE.json과 원 코드 계보.
- inputs/PHYS22_INITIAL_COEFFICIENTS.json 및 선택 소스 snapshot.
- 재현·게시 기록은 실제 수행한 범위만 이어받는다. Git 문서 projection을 완전한 ZIP 복원으로 간주하지 않는다.

고정 계약 SHA256은 7fce1d8729a22b89b00d8116d237af3ddcddc0951901eaa46ba821d9ed07b1c3, J 입력 SHA256은 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79다. 파일명을 통해 결과를 추정하지 말고 이 입력과 실제 판정·원 결과를 읽는다.

## 3. 그대로 유지할 물리·수학 계약

\[
I=[a,b]=[13.61,24.58]\ {\rm eV},\quad m=18\ {\rm eV},
\quad dP=d\nu_0/N_0,
\]

\[
P\ge0,\quad\int dP=1,\quad\int E\,dP=m,\quad
\int(E-m)^2dP=W.
\]

\(P\)는 Borel 확률측도이며 델타 선을 허용한다. \(W\)의 단위는 eV², 응답 \(A(P)=\int k\,dP\)의 단위는 s\(^{-4}\)다. \(k\)는 고정 \(qN_0/45\) 정규화를 이미 포함한다. 허용 분산은

\[
0\le W\le W_{\max}=(m-a)(b-m)=28.8862\ {\rm eV}^2.
\]

초기 기체·광자 수·기하·원자 적합식·source binary64 리터럴의 정확한 실수 해석·직렬화 J를 유지한다. Metric \((-+++)\), proper seconds, \(w\) in eV/H, \([\epsilon^2]=\tfrac12\partial_\epsilon^2|_0\), 시간계수에 추가 factorial 없음도 유지한다. \(J\)의 오차를 새로 둘러싸는 문제는 이 한 루프에 섞지 않는다.

## 4. 목표 결과와 검토할 두 경계 후보

각 \(W\)에서

\[
\mathcal A(W)=
\left\{\int k\,dP:\int dP=1,\ \int E\,dP=m,\
\int(E-m)^2dP=W\right\}
\]

의 정확한 상단·하단과 그 등호 측도를 구한다. 허용집합의 볼록성과 콤팩트성 때문에 달성된 두 극값 사이가 응답 구간인지도 명시한다.

검토할 자연스러운 후보는

\[
v_W=m+\frac{W}{m-a},\qquad
P_W^a=\frac{v_W-m}{v_W-a}\delta_a+
       \frac{m-a}{v_W-a}\delta_{v_W},
\]

\[
u_W=m-\frac{W}{b-m},\qquad
P_W^b=\frac{b-m}{b-u_W}\delta_{u_W}+
       \frac{m-u_W}{b-u_W}\delta_b.
\]

두 측도 모두 같은 질량·평균·분산을 만족한다. **\(P_W^a\)가 응답 상단이고 \(P_W^b\)가 하단인지 여부는 다음 루프에서 증명할 후보**다. PHYS25의 최소 분산 dual 한 개를 모든 \(W\)에서 달성되는 정확한 envelope로 오해하면 안 된다.

기존 \(k'''<0\)를 사용한 이차 Hermite 보간 잔차나 동등한 연속구간 dual이 유망하다. 양 끝점·내부 접촉의 부호 방향, \(W=0\)에서 단색으로 합쳐지는 경우, \(W=W_{\max}\)에서 양 끝점 혼합이 유일해지는 경우, 모든 등호 조건을 따로 확인한다. 격자 LP의 결과만으로 최적성이나 지지 구조를 선언하지 않는다.

## 5. 다시 계산할 필요가 없는 닫힌 결과

고정 커널의 \(k''>0\)와 PHYS25의 \(k'''<0\)는 닫힌 입력이다. PHYS25의 최소 경계는

\[
V_*\simeq16.339944654589707345109\ {\rm eV}^2
\]

이며 정확한 정의는
\((v_*-m)k(a)+(m-a)k(v_*)=0\)의 유일근이다.

오른쪽 끝점 고정 경로의 영 응답 근과 비교 분산도 이미 수치 원 결과에 있다.

\[
u_0\simeq14.440696201770001068068\ {\rm eV},\qquad
W_0\simeq23.420218992353392972114\ {\rm eV}^2.
\]

이 수치는 PHYS25에서는 한 비교 경로의 영점이다. 이를 전체 응답 하단의 영점 또는 두 번째 전역 부호 경계로 승격하려면 위 극값 정리가 필요하다. 기존 수치 bracket과 소수를 interval 인증이나 물리적 오차 경계로 재분류하지 않는다. PHYS25의 유한 중점은 작은 음의 잔차를 가지며, 정확한 영점으로 정의한 law와 구별해야 한다.

기존 PHYS19–25 main과 닫힌 proof suite, 기존 근 반복을 다시 실행해서 시작하지 않는다. 필요한 helper는 실제 읽은 범위와 소스 identity를 기록하고 명시적으로 적응하거나 입력의 순수 계산부만 재사용한다. 과거 원 결과 파일을 덮어쓰지 않는다.

## 6. 승인된 다음 작업의 범위와 예산

범위는 위 한 질문에 대한 직접 수학 유도, 실제 고정 커널과의 조건 연결, 필요한 최소 수치 검산, 별도 독립 최종 판정, 보고·재현·다음 handoff·동일 브랜치 additive 문서 게시다.

먼저 증명과 필요한 검사 설계를 고정한다. 새 수치 검산이 필요하다면 미리 고정한 소수의 내부 분산과 퇴화 끝점에 대한 모멘트·보간 접촉·서로 다른 원식 미분 또는 잔차 경로 검산으로 제한한다. 기본값으로 새 root search와 새 도함수 부호 campaign은 0이다. 기존 근 수치로 해결되지 않는 정확한 추가 질문이 있을 때만 범위와 이유를 명시해 필요한 새 국소 계산을 설계한다. 전 에너지·전 분산 dense scan이나 대규모 LP sweep은 하지 않는다.

물리·수학 candidate 생성자와 검증 설계자에서 분리된 실제 final reviewer가 최종 PROMOTE를 판정한다. 공유 입력·기존 결과 노출·helper 계보를 실제대로 기록한다. Full-history를 받았으면 NONBLIND다. Owner의 역할 변경은 독립 판정이 아니다.

첫 실패·검사 예산·변경 이유를 보존하고 결과를 본 뒤 조용히 허용오차를 완화하지 않는다. 재현 replay는 새로 작성한 과학 프로그램에만 제한하고 독립 물리 검증과 합산하지 않는다.

## 7. 완료 기준과 보존 상태

완료에는 다음이 필요하다.

1. \(W\)별 정확한 응답 구간과 등호 측도, 또는 미해결 부분이 분명한 엄밀 상·하계.
2. 분산의 각 영역에서 모든 스펙트럼에 강제되는 부호와 양·음 공존 가능성의 정확한 양화.
3. \(W=0\), \(W_{\max}\), 영 응답 경계의 퇴화·유일성 처리.
4. 새 수학 주장과 수치 근사·구현 검산의 분리, 상속 입력의 무단 재승격 없음.
5. 독립 최종 판정, 원 증거·DAG·상태·단일 후속 질문·재현 묶음.
6. 현재 branch의 최신 head를 확인한 additive docs commit과 nonforce expected-head CAS 게시; 소스 트리 보존을 실제 readback으로 확인.

기존 다음 루프 요청과 같은 branch 문서 게시 권한을 이어 사용한다. 새 PR merge나 타인에게 메시지 전송은 포함하지 않는다. 다른 branch로 옮기거나 기존 파일·이력을 덮어쓸 필요가 생기면 먼저 변경 이유와 권한 범위를 판단한다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. Native·gas IVP·생산 source/default/runtime 변경은 0으로 둔다. 유한 시간·유한 \(\epsilon\) remainder, 물리 방출원 admission, 독립 원자 데이터, 모든 평균의 2차원 phase diagram, 세계 최초성은 이 계약에서 주장하지 않는다.
