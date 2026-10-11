# PHYS29 다음 물리 연구 루프 — 작은 대역폭의 이차 문턱 이동 분해

상태: **PROPOSED / NOT_RUN**. PHYS28의 다음 한 질문이며 PHYS29의 실행·유도·판정 증거가 아니다.

## 1. 다음에 답할 한 질문

**같은 실제 광자 분산 W에서 두 문턱의 이차계수 d*,d0를 정당하게 구해, 균일 대역 평균화와 V=W−δ²/3 보정이 지원 끝점·내부 중심·확률의 이차 이동과 어떻게 합쳐지는지 분리할 수 있는가? 그 이차식은 이미 계산된 PHYS27 δ=.05의 PHYS28 선형 잔차를 얼마나 설명하는가?**

명칭: **PHYS29_SMALL_WIDTH_SECOND_ORDER_DECOMPOSITION**. 이차계수의 부호·비영성을 사전 가정하지 않는다. 새로운 평균·지원구간·J·폭 root campaign으로 확대하지 않는다.

## 2. 실제 PHYS28에서 시작

PHYS28은 δ=0의 고정 실제 W 우미분 B±를 모든 endpoint·이동 중심·확률 항을 포함하여 유도했다. T(x,y)=(y−x)⁻¹∫(E−x)(y−E)k‴(E)dE<0를 통해 B+<0,B−>0가 나왔고, C±=∂WA0,±>0와 물리 반영역의 한쪽 근 논증으로 c*=−B+/C+>0,c0=−B−/C−<0를 정당화했다. 고정 중심의 대칭 평균화와 V′(0)는 모두0이다. 정량 나머지나 이차계수는 아직 구하지 않았다.

- c*≈5.71638089140 eV, c0≈−2.37494837006 eV.
- PHYS27 δ=.05의 실제 이동−선형 예측: +0.00369532482000 및 −0.000605391537981 eV².
- 실제 이동 대비 절대잔차: 1.27638736129%, 0.507228558567%.
- 공존폭 감소량 잔차: +0.00430071635798 eV², 실제 감소량의 1.05186147833%.
- 첫 Decimal80 main1회120/120 PASS, 고정4노드×2경로=8 joint(k,k′) 평가. 별도 경로 replay1회 결과 byte동일. 새 물리 root와 old PHYS19–27 main/suite/root 모두0. 재현의 독립 물리 credit0.

| 핵심 입력 | SHA256 |
|---|---|
| PHYS28 PHYSICS_CONTRACT.json | d9c50cb43d60bf466eb92e91e8e62791fcf84680025c34fc0c42c899ed16fde2 |
| PHYS28 새 numerical code | 1e3276730868b0062d5c8773f8a111005108220c4b107f0144d5d5b6d2f7a72e |
| PHYS28 SMALL_WIDTH_FIRST.json | 563e52f9ed2dec6ef379a2e26ca3ec14d06679fef02c2bd0c7328e3022182c84 |
| PHYS28 최종 numerical PROTOCOL | 5298c389da5ddd7eb2a5246c3cb472faba93c7d97a39efe7ee99de441200b56a |
| PHYS22 J 원자료 | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |

최종 승격 범위·조건은 `independent/DECISION_REVIEW.json`, 최종 ZIP·source·게시 commit은 **분리된 PHYS28_PUBLICATION_RECEIPT.json**에서 실제로 읽는다. 이 인수문 작성 시 독립 판정을 선제 완료 주장하지 않는다. intake head는4d95fe98dd1b1fc1bff0054d5bc36a7861ea1a70, scientific source subtree는cb69b4736dd046e4675557577eb8e0ead037d1f3였으며 다음 실행에서는 최신 actual head/source와 대조한다.

## 3. 이론 계약과 가능한 계산식

원래 a=13.61,b=24.58,m=18 eV, L4.39,H6.58, source-real 상수와 직렬화 J를 유지한다. 실제 분산 W와 중심 분산 V=W−δ²/3, alpha=a+δ,beta=b−δ,ell=L−δ,h=H−δ,fδ(c)=균일평균을 모두 함께 처리한다. PHYS27의 정확 Aδ,±와 PHYS28 일반 B/C 식을 소비한다. 정확근에서의 식과 저장된 수치근에서의 근사평가를 구분한다.

목표 형태는 Wj(δ)=wj+cjδ+djδ²+o(δ²)다. dj는 Wj″(0)/2로 정의하며 full second derivative와 혼동하지 않는다. 필요한 정칙성과 실제 허용 근방을 먼저 확인한 뒤, 암묵식의 이차 미분을 사용한다면

\[
d_j=-\frac{F_{\delta\delta}+2F_{\delta W}c_j+F_{WW}c_j^2}{2F_W}\bigg|_{(0,w_j)}
\]

를 검증 대상의 출발 형식으로 둘 수 있다. 이 문서가 그 편미분이나 적용 조건을 이미 계산·검증했다는 뜻은 아니다. 고정 중심 평균화, V″(0)=−2/3, 경계·중심·확률의 직접 이차항과 근 자체의 이동에 따른 교차항을 구별한다. 원 지원의 끝에서는 물리적으로 허용되는 경로 미분을 유지한다.

계수의 단위는 무차원(eV²/eV²)이어야 한다. 새 이차근 전개가 정당하더라도 수치적 나머지 상계와 유효 폭 인증은 별개다. .05 한 폭의 잔차 개선을 수렴률 인증으로 올리지 않는다. 다른 양의 폭 사이의 분포족 포함이나 전역 폭 단조성을 가정하지 않는다.

## 4. 새 가벼운 수치를 쓸 경우의 제한

실제 다음 루프 요청 이후 새 계약·수식·정칙성·source/J/저장근·정밀도·두 대수 경로·허용오차를 실행 전에 고정한다. 필요한 k″까지 공동 산출한다면 실제 읽은 순수 log-Taylor식을 명시적으로 적응할 수 있으나 옛 모듈을 import하거나 main을 실행하지 않는다. k″의 계산 경로와 필요한 log 미분 차수를 직접 점검하며 PHYS28의 k,k′ 코드를 이름만 바꾸어 k″ 검증 완료로 삼지 않는다.

- 새 과학 main 최대1회. **새 물리 영점 탐색0회**.
- old PHYS19–28 main/suite/root 재실행0회.
- 새 kernel/derivative joint 평가 최대24개. 평가당 k,k′,k″ 산출수도 별도로 기록한다. 기존 원근으로 정해지는 고정4노드와 두 대수 표현을 우선하며 별도 폭·근 sweep은0회.
- PHYS24/25의 닫힌 도함수 부호 인증 campaign, native, gas IVP, dense LP 모두0회.
- PHYS27 δ=.05 원근과 PHYS28 일차계수·잔차는 원 JSON에서 읽어 소비한다. 새 폭 root 또는 기존 root refinement로 대체하지 않는다.
- 새 프로그램이 있으면 별도 경로 replay1회만 수행하며 추가 평가와 main을 실제로 계수한다. 독립 물리 credit0.
- 첫 실패와 사전 동결 변경을 보존한다. 사후 허용오차 완화·숨은 추가 실행·이름 변경을 통한 예산 초기화는 하지 않는다. 새 문제가 이 예산으로 해결되지 않으면 주장 범위를 줄이고 실제 blocker를 기록한다.

## 5. 종료 기준

정확 이차 미분식·정칙성·고정 실제 W의 처리·항별 분해·단위·원근 분모 조건을 남긴다. 새 수치가 있으면 첫 raw stdout/stderr/exit/UTC/실제 counts와 두 표현 비교, 기존 한 폭에 대한 이차 예측 진단을 남긴다. 생성자와 검증 설계자가 아닌 **distinct NONBLIND 최종 판정자**, 새 프로그램 재현, 재현 가능한 묶음, 의미 있는 한계와 다음 한 질문까지 완결한다.

현재 채택 모델의 research 하네스와 코드 개발에 필요한 대응 coding 하네스를 실제로 읽고 적용한다. 템플릿 상태는 연구 실행의 증거가 아니다. 이 대화 안의 assistant cloud에서 독립 유도·코드·가벼운 검증을 수행하며 사용자 컴퓨터의 local Codex로 보내지 않는다.

## 6. 기존 권한과 보호 상태

사용자의 다음 연구 루프 요청과 기존 세션의 같은 branch additive docs 게시 권한을 유지한다. `cosmosapjw-quantum/rei_bianchi`, `forward/rust-reion-kernels-20260922`, PR83 draft의 새 PHYS29 docs prefix만 추가한다. 최신 head를 실제 읽고 expected-head nonforce CAS, 기존 경로/source 보존 및 선택 readback을 수행한다. 최종 영수증은 hash cycle을 피하여 분리한다. merge·production source/default/runtime 변경·타인에게 메시지 전송 권한은 포함하지 않는다. 저장 성공 확인을 원격 ZIP 전체 복구로 부르지 않는다.

이 lane은 fastest-track 이론·가벼운 수치다. **Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED**를 유지하며 BASS_HE/bass_cr/WU088_HH 별도 atomic lane을 활성화하지 않는다. 초기 계수 연구와 실제 emitter·history admission을 구분한다.
