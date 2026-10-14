# PHYS30 다음 물리 연구 루프 — 대칭 대역 프로파일의 이차계수 의존성

상태: **PROPOSED / NOT_RUN**. 이 문서는 다음 한 질문의 인수 계약이며, PHYS30을 이번 PHYS29 안에서 실행·유도·승격했다는 증거가 아니다.

## 1. 다음에 답할 한 질문

**균일 대역을 같은 외곽 지원 \([-1,1]\)의 고정 대칭 확률 프로파일 \(\nu\)로 바꾸고 같은 중심 허용구간을 유지하면, 일차 문턱계수 c는 그대로이고 이차계수 d의 프로파일 의존성은 \(\mu_2=\int z^2\,d\nu(z)\) 하나로 결정되는가?**

명칭: **PHYS30_SYMMETRIC_PROFILE_SECOND_ORDER_UNIVERSALITY**. 새로운 평균·지원구간·J·물리 root campaign으로 확대하지 않는다. 같은 이차 모멘트의 프로파일이 유한 양의 폭에서도 같은 응답·근을 준다는 질문은 포함하지 않는다.

## 2. 실제 PHYS29에서 출발

PHYS29은 실제 W를 고정하여 \(V=W-\delta^2/3\)를 유지한 한쪽 C² 근 전개와

\[
d=-\frac{F_{\delta\delta}+2F_{\delta W}c+F_{WW}c^2}{2F_W}
\]

를 정확 내부 단순근·정칙성 전제 아래 유도했다. 전체 이차미분과 Taylor 이차계수의 2배 차이를 구별한다. 균일 평균은 \(d_{\rm avg}=-(pk''_e+qk''_x)/(6C)\), 실제 분산 보정은 \(d_V=1/3\)이며 끝점·내부 중심·확률의 기하 항과 두 암묵근 항까지 분리했다. 공통 \(1/3\)은 간격의 이차계수에서 상쇄된다.

- 저장 수치근에서 \(\widehat d_*\approx1.45408210662\), \(\widehat d_0\approx-0.245144110608\), 무차원.
- \(\widehat c_*\approx5.71638089140\,\mathrm{eV}\), \(\widehat c_0\approx-2.37494837006\,\mathrm{eV}\).
- PHYS27 반폭 .05 eV의 실제−이차 예측 잔차는 상단 +0.0000601195534502, 하단 +0.00000746873854034 eV². 실제 이동 대비 0.0207656544222%, 0.00625769811182%다.
- 하단 이차항은 기존 선형 잔차를 101.233703822% 보정하여 잔차 부호가 양수로 바뀌었다. 이차 잔차 개선은 판정 조건이 아닌 관측 진단이다.
- 간격 이차계수 \(d_0-d_*\approx-1.69922621723\). 간격 감소량의 실제−이차 예측 잔차 +0.0000526508149098 eV², 실제 감소의 0.0128772416957%.
- 새 첫 Decimal80 main 1회 238/238 PASS, 별도 경로 replay 1회 238/238 PASS, raw byte·JSON 동일. 합계 main2, joint(k,k′,k″)16, k16·k′16·k″16, 새 물리 root 및 old PHYS19–28 main/suite/root/import0. 재현의 독립 물리 credit0.

| PHYS29 핵심 입력 | SHA256 |
|---|---|
| PHYSICS_CONTRACT.json | 603e2a30074800edd2226c86cf1f256efe5fd49ad45a2252788059d19a487d10 |
| SOURCE_MANIFEST.json | c240b00671a0fa12f3ea6b4029116ad4b7f67d845dc59090ebb82fb91a32d08a |
| contributions/theory/DERIVATION_KO.md | 764cddda1c8af278995be4bf02476acefa82ecfbfff88699daebf30d524dd9f1 |
| contributions/numerics/second_order_width.py | faf7c3911d54f9739b4d486f88fa388af7165c50684bfbb036dcf02e5a8c5bda |
| contributions/numerics/PROTOCOL.json | 6ab5d3c488a00ebfb868e4d4e83d98a2fe1db9479956b587f673d9d9b86e7573 |
| contributions/numerics/SECOND_ORDER_FIRST.json | 40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f |
| portability/REPLAY_RECEIPT.json | ed754b4d43ad8cc231a2b16edb61eda491dfa7582a7939040aa9edb7ee64d0e9 |
| PHYS22 J 원자료 | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |

최종 승격 여부·정확한 범위는 실제 `independent/DECISION_REVIEW.json`, 연구 종료는 `state/CLOSEOUT.json`, 최종 ZIP·현재 source·게시 commit은 **분리된 PHYS29_PUBLICATION_RECEIPT.json**에서 읽는다. 이 인수문은 판정 전 작성되므로 그 결과를 선제 완료 주장하지 않는다. intake head는 `eea60e380f79b016c667b0621db429f07c5fdefd`, scientific source subtree는 `cb69b4736dd046e4675557577eb8e0ead037d1f3`였다. 다음 루프에서는 최신 actual head/source와 실제 전송 ACK를 확인한다.

## 3. 다음 이론 계약

a=13.61,b=24.58,m=18 eV, L4.39,H6.58, source-real 상수, PHYS22 전체 직렬화 J와 기존 영폭 근을 유지한다. \(\nu\)는 다음 조건을 만족하는 고정 확률측도로 둔다.

- \(\nu\geq0\), \(\nu([-1,1])=1\), 대칭이고 \(\mu_1=\int z\,d\nu=0\).
- \(\nu\)는 \(\delta,W\), 대역 중심, 두 branch에 의존하지 않는다.
- 외곽 지원 한계는 \([-1,1]\), 중심 허용구간은 **같은 \([a+\delta,b-\delta]\)**다.
- 실제 분산은 W이고, 다음에는 \(V=W-\mu_2\delta^2\)를 일관되게 사용한다.

검증할 평균은

\[
f_{\delta,\nu}(c)=\int_{-1}^{1}k(c+\delta z)\,d\nu(z).
\]

분포족·경계식은 위 평균과 V를 사용하도록 명시해야 한다. PHYS27에서 균일 평균에 대해 구한 결과를 일반 프로파일에 자동 승계하지 않는다. 필요한 평균 kernel의 미분 부호, 모멘트 보존과 지원 조건, 정확 내부 단순근 근처의 물리 한쪽 C² 논증을 새로 정당화한다. compact support의 고정 측도라면 적분 미분에 프로파일 밀도의 매끄러움이 반드시 필요한지 검토할 수 있지만, 그 결론도 다음 루프의 증명 대상이다.

가능한 목표식은 다음과 같다. 이 식은 **다음에 검증할 후보**이며 이번 PHYS29의 승격 주장에 추가하지 않는다. PHYS29 영폭 표기 \(C=F_W\), \(p,q,e,x\)를 유지할 때

\[
c_\nu\overset{?}=c_{\rm uniform},\qquad
d_\nu\overset{?}=d_{\rm uniform}
+\left(\mu_2-\frac13\right)
\left[1-\frac{pk''_e+qk''_x}{2C}\right].
\]

이를 위해 영폭의 B,C,M,N과 기하 항이 왜 프로파일에 무관한지, \(F_{\delta\delta}\)의 프로파일 항이 어떤 형태인지 확인해야 한다. 결과의 부호나 두 예시의 순서를 사전 통과 조건으로 삼지 않는다.

## 4. 중요한 적용 경계

프로파일이 실제로 ±1에 닿지 않으면 \(\delta\)는 공통 **외곽 반폭 한계**이고 그 프로파일의 실제 반폭과 다를 수 있다. 실제 지원이 좁다고 중심 허용구간을 넓히면 끝점 이동과 일차계수까지 달라지는 별도 계약이다. \(\mu_2=0\)인 중심 원자 프로파일에서도 이 인수 계약에는 중심 허용구간의 축소가 남는다.

원자 측도를 허용하면 광자 law의 절대연속성을 자동으로 주장할 수 없다. 밀도에 관한 물리 결론이 필요하면 \(\nu\ll\mathrm{Lebesgue}\)를 별도로 고정한다. 이번 다음 질문은 프로파일 불변성의 국소 이차 구조다. 모든 양의 폭의 strict containment, 유한폭 root 동일성, 폭 전체의 단조성, Taylor 나머지 상계로 확대하지 않는다.

평균 0은 일차 비교에 핵심이다. 비영 평균 프로파일은 실제 평균을 바꾸므로 같은 식을 적용하지 않는다. 대칭보다 약한 가정으로 확대할 가능성이 보이더라도 현 루프는 고정 대칭 프로파일의 한 질문으로 유지한다.

저장 수치근에서 남은 응답 A를 그대로 유지한다. 그 점의 일반 미분식은 동일 A-level 계수이고, 정확 영점 계수의 정리는 A=0의 정확근 전제 아래다. 새 근 탐색·보정 없이 이 구별과 원래의 수치 불확실성 한계를 보존한다.

## 5. 실행 예산과 종료 기준

사용자가 다음 루프를 실제 요청하면 현재 모델의 연구 harness와 필요한 coding harness를 읽고 계약을 먼저 동결한다. 이번 목표는 PHYS29에 이미 저장된 k,k′,k″와 편미분·가중치로 다룰 수 있는지 우선 판단한다.

- **새 물리 kernel·도함수 평가0, 새 물리 root0.** PHYS29의 네 노드 값과 실제 raw를 읽는다.
- old PHYS19–29 main/suite/root/import 재실행0. 이전 루프 예산을 이름 변경으로 초기화하지 않는다.
- 선택적 새 수치 main은 cached 값의 명시적 대수 조합만 최대1회. 예를 들어 균일 \(\mu_2=1/3\)과 삼각형 \(\mu_2=1/6\)을 비교하려면 프로파일 정의·정규화·모멘트·두 표현·허용오차·실제 counts를 먼저 동결한다. 이 예시 계산은 아직 수행하지 않았다.
- 새 프로그램이 있으면 별도 경로 replay 최대1회, 독립 물리 credit0. replay에도 새 물리 kernel/root는0이다.
- 유한차분·quadrature·폭 sweep·닫힌 도함수 부호 campaign·native·gas IVP·dense LP는0.
- 첫 실패와 사전 변경을 보존하며 사후 허용오차 완화나 숨은 추가 실행을 하지 않는다. 필요한 문제가 이 계약으로 닫히지 않으면 실제 blocker와 주장 축소를 기록한다.

종료에는 프로파일 전제·지원·정칙성·고정 실제 W·식의 증명 범위, 선택적 cached 진단의 실제 raw와 실행 이력, 생성·검증 설계자가 아닌 distinct NONBLIND 최종 판정, 필요한 단일 재현, 완전한 묶음과 다음 한 질문을 포함한다. 템플릿 상태는 실행 증거가 아니다. assistant cloud의 이 대화 안에서 처리하며 사용자 컴퓨터의 local Codex나 무거운 물리 계산으로 보내지 않는다.

## 6. 권한과 보호 상태

현재 다음 루프 요청과 기존 세션의 같은 branch additive docs 게시 권한을 유지한다. `cosmosapjw-quantum/rei_bianchi`, `forward/rust-reion-kernels-20260922`, PR83 draft의 **새 PHYS30 docs prefix**만 추가하는 범위다. 최신 head를 실제 읽어 expected-head nonforce CAS를 사용하고, 모든 기존 경로·scientific source·선택 바이트 readback을 확인한다. 최종 게시 영수증은 hash cycle을 피하여 분리한다. merge·production source/default/runtime 변경·타인에게 메시지 전송 권한은 포함하지 않는다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED**를 유지한다. BASS_HE/bass_cr/WU088_HH 별도 atomic lane을 활성화하지 않는다. 초기 응답 계수의 연구와 실제 emitter/history admission을 구별하고, 저장 성공을 원격 ZIP 전체 복구의 증거로 부르지 않는다.
