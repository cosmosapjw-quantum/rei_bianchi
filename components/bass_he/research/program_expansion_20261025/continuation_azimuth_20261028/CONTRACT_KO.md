# AZIMUTH09 — 유한 방위각 공동 검출 사건

## R1/C1: 목표와 출발점

사용자의 2026-10-28(KST) 새 요청은 최신 branch/repo/접근 가능한 대화/백업 조사를 종합한 다음 이론 R1–R10 및 코딩 C1–C10 한 단위의 실제 수행, 매 단계 source 게시·Drive/Dropbox ACK, DAG 수와 복사용 인계를 승인한다. 이 단위는 **HE-EXP-AZIMUTH-09**다.

선행 최종 권위는 `externaldelivery_kinematic08`의 게시 후 네 문서다. Local D10 `b3ac835c3fa0b1aa09606ab6e8cfdc08699bab25`, remote P10 `e56573a5961623c49428f6f8d566fb13edf8a6b9`, exact tree `0bc4f06d711fd30e8d7d71e2dc2d69ec2bf2e363`. 실제 과학 source는 Local S05R `d004212d560907eb4058d9539eec8e9b262ec406` / remote same-tree `391f1e4c356082c0b5cc693d49fb2aef873a0f2a`다. 선행 14/14 PASS, plot CPU 7.040661/6 s FAIL, workflow PARTIAL, reserve 0을 유지한다. 이전 science/test/plot을 재실행하지 않는다.

기존 로컬 8 complete +1 partial +3 physical open /12에 새 실제 계산 노드 한 개를 추가한다. 시작 **8 complete +1 partial +1 pending +3 physical open /13**. 중앙 최신 intake `b99a9468abd53de77ddae36d93180e60072885bc`, **28/88**, HE completion delta 0. Reference node의 완료와 중앙 물리 closure는 별개다.

## 실제 연결과 범위

정지 bare alpha의 `gamma+alpha -> d+d`, signature `(-,+,+,+)`, `A=m_alpha*c²`, `M=m_d*c²`, `e=E_gamma`(MeV)를 사용한다. c를 rest-energy 정의와 q=cp에 유지한다. ħ와 k_B는 이 고전적 운동학·각도 측도 계산에 들어가지 않는다. 정확히 선언한 scalar와 `0<A<2M`, `H=A²+2Ae-4M²>0`의 KINEMATIC08 정의역을 재사용한다.

새 연결은 `t=phi/(2*pi) mod 1`과 두 딸입자 사이의 반회전이다. Plus 방향은 `(F(mu),t)`, minus 방향은 `(F(-mu),(t+1/2) mod1)`다. Lab polar cosine을 임의로 `-F(mu)`로 대체하지 않는다. z boost는 transverse momentum을 보존하므로 두 transverse 방향이 반대인 사실이 그대로 유지된다. μ=±1의 방위각과 정지 endpoint는 연속 측도의 영집합으로 처리한다.

입력 측도는 **명시적으로 선언한** `dSigma=rho(mu) dmu dt`다. rho는 비음수 degree≤8의 짝 Bernstein polynomial이며 sigma=∫rho dmu. `azimuth_law="UNIFORM_DECLARED"`를 API에서 명시해야 한다. 원 M0475002의 polarization/azimuth/사건 정규화를 이 가정으로 확정하지 않는다. dΩ=dμdφ이므로 이 선언에서 `dSigma/dΩ=rho/(2*pi)`이나, empirical DCS 값을 입력 rho로 변환하는 작업은 이번 범위에 없다.

검출기는 유한 개의 `(polar cosine window) × (rational-turn arc)` 합집합이다. Arc는 `(start,width)`, `0≤start<1`, `0≤width≤1`; width0는 empty, width1은 fullcircle다. Seam crossing은 정확히 두 interval로 나눈다. Detector당 patch≤8, 두 detector 합계≤16, 활성 서로 다른 polar window N≤8. 중복·접촉·겹침은 합집합이며 double count하지 않는다. 일반 원형 telescope의 정확 shape나 효율 응답은 이 직사각형 입력을 별도로 공급해야 한다.

## 출력과 수용 기준

동일한 `(mu,t)`에서 `Ap,Am,Bp,Bm`를 계산한다. 서로 다른 두 딸입자의 coincidence는

`C=(Ap intersect Bm) union (Bp intersect Am)`.

한 검출기의 hit는 `Ap union Am`, inclusive daughter count는 `1_Ap+1_Am`. Detector A/B가 겹칠 수 있으므로 `hitA intersect hitB`와 C를 구분한다. Assignment sum은 두 conjunction의 합이고 C는 OR이다. 결과는 사건 measure Y, hit, inclusive, double-hit, assignment overlap, C|hit의 조건부 경계, selected daughters 2Y와 pair total energy GY, label별 coincidence energy GY/2를 제공한다. 마지막 두 에너지 등식은 짝 rho와 label-exchange 대칭에서 유도한다. Rest energy가 포함된 GY를 deposition/heating으로 넣지 않는다.

정확한 φ strip 경계마다 활성 polar SetBounds를 합성한다. KINEMATIC08의 창 하나 uncertain length≤5δ를 사용한다. N개의 창과 reflection의 합집합 U 밖에서는 모든 Boolean event가 exact이며 `|U|≤10Nδ`. 따라서 event measure width≤10NBδ, B는 **최대 Bernstein 계수에 의한 밀도 상계**다. Default `δ=sigma/(10NB*2^40)`이면 각 event width≤sigma*2^-40. N≤8,n≤8에서 root당 최대 50 bisections. Inclusive/assignment 합의 폭은 각각 두 성분 bound의 합을 따르며 event와 동일 epsilon을 일괄 적용하지 않는다. 수동 δ는 반환된 실제 width/width_bound를 따른다. Conditional ratio는 denominator lower>0일 때 `[Lnum/Uden, min(1,Unum/Lden)]`; denominator0은 undefined, lower0<upper는 unresolved이며 null bounds. Ratio에 무조건 동일 epsilon을 약속하지 않는다.

완료 조건은 새 코드의 한정된 정확 포함 정리·독립 검토·새 suite·저장 데이터 plot/resource gate·단계별 실 ACK·정확한 외부 인계다. 과학/자원 실패는 그대로 기록하고 부분 완료를 상향하지 않는다. 기존 세 physical input은 유지한다: 원 정규화/liquid-He response, 완전 각분포·실제 photon encounter flux/history, named nonthermal birth/deposition/thermalization·global species binding. Binding 단일 owner `population_rest_energy_witness`; independent binding RHS/Gamma_thermal/Cv/species_heating/thermal_deposition null, birth_pool UNASSIGNED, global physical completion null, L4 false, production NOT_APPROVED.

## 자원·역할·종료

새 단위만의 validation CPU12s/wall40s/AS512MiB, singlethread, initial suite1회와 진단된 targeted repair reserve1회. Plot은 같은 validation에서 저장한 데이터만 사용하며 CPU8s/wall20s/AS512MiB, 최초1회, science calls0. 이 새 plot cap은 선행 cold-start 전체7.040661s 관측과 새 작업 크기를 참고하여 **실행 전에** 고정한 별도 AZIMUTH09 예산이다. KINEMATIC08의 6s 기준과 FAIL, 소진 reserve를 변경·이전하지 않는다. Wolfram evaluator는 새 식 검산1회/timeConstraint15s, 실제 remote CPU는 제공된 경우만 기록한다. Context 검색은 evaluator 실행과 구분한다.

Astra controller는 이론/계약/판정을, lower-tier coding agent는 구현·제한 실행·기계적 포장을, 독립 Astra reviewer는 같은 pass의 수학→코드→실제 결과 검토를 맡는다. 기존 helper를 새로운 단위용으로만 복제한다. 원 tree·과거 실패·raw 결과를 보존하고 변경된 의존성만 검증한다. 마지막 R10/C10과 실제 delivery ACK 뒤 새 노드·예산·재실행을 시작하지 않는다.
