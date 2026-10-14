# PHYS27 단일 후속 handoff — 유한 선폭에서의 응답 구간

과제 후보: PHYS27_FINITE_WIDTH_RESPONSE_ENVELOPE  
선행 연구: REI-PHYS26-20261011  
상태: **다음 루프의 계약 후보다. PHYS27 계산이나 판정을 실행한 결과가 아니다.**

## 1. 다음 한 문장 질문

**델타 선을 반폭 0.05 eV의 균일 대역으로 제한했을 때, 평균 18 eV·분산 고정 HeIII 초기 응답의 정확한 상·하한과 두 부호 경계는 어떻게 달라지는가?**

PHYS26은 모든 Borel 광자 수 확률측도, 델타 선 허용이라는 계약에서 완전한 응답 구간을 구했다. 그 상·하한을 달성하는 측도는 두 델타 선이다. 다음에는 유한 선폭을 가진 명시적인 분포족에서 이 결과가 어떻게 변하는지 확인한다. 실제 방출원 모형 전체나 임의의 연속 스펙트럼을 대표한다고 주장하지 않는다.

## 2. 실제로 읽고 소비할 선행 입력

Repository는 cosmosapjw-quantum/rei_bianchi, branch는 forward/rust-reion-kernels-20260922, draft PR은 83이다. PHYS26 입력 head는 2c5fb6b89908e5ac91395aeef8558b728bd4ce7b, 과학 소스 tree는 cb69b4736dd046e4675557577eb8e0ead037d1f3다. 새 PHYS26 게시 커밋은 이 handoff 동결 뒤에 생기므로 추측하지 않는다. 다음 시작 시 PHYS26_PUBLICATION_RECEIPT.json과 실제 최신 head·commit·tree를 읽어 확인한다.

필수 입력은 PHYS26의 PHYSICS_CONTRACT.json, SOURCE_MANIFEST.json, report/PHYS26_REPORT_KO.md, PHYS26_RESULTS_SUMMARY.json, contributions/theory/ENVELOPE_DERIVATION_KO.md, THEORY_CLAIMS.json, independent/DECISION_REVIEW.json과 판정문, 원 수치 코드·결과·실행 기록이다. inputs/PHYS22_INITIAL_COEFFICIENTS.json 및 상속한 PHYS24 곡률과 PHYS25 세 번째 도함수의 닫힌 증거도 소비한다. 기존 전체 패키지를 재실행하지 않는다.

유효한 PHYS26 계약 SHA256은 d4ff7556332f75447d93e0c6a8da4a0d96cb8a86b257f111809d388b7f2b80ce, J 원 입력 SHA256은 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79다. PHYS26의 initial metadata 보존 파일을 현재 계약으로 오해하지 않는다. 보고서의 최종 판정 범위와 detached 완료 receipt를 함께 읽는다.

현재 바이트가 정확히 남아 있으면 알려진 manifest·크기·SHA와 필요한 최신 Git blob만 확인하여 소비한다. 메타데이터로 확인한 업로드·게시와 원격 ZIP의 완전 복원은 구별한다. 같은 문서를 반복 다운로드하는 절차를 새 물리 증거로 세지 않는다.

## 3. 제안하는 유한 선폭 계약

기존 지원구간과 평균은
\[
[a,b]=[13.61,24.58]\ {\rm eV},\qquad m=18\ {\rm eV}
\]
로 고정한다. 반폭은 정확한 십진 값
\[
\delta=0.05\ {\rm eV}
\]
하나만 사용한다. 중심 에너지 \(c\)에 대한 비음수 Borel 확률측도 \(Q\)를
\[
c\in[a+\delta,b-\delta],\qquad \int c\,dQ(c)=m
\]
에 두고, 실제 광자 에너지 분포를
\[
p_\delta(E)=\frac1{2\delta}
\int {\bf1}_{|E-c|\le\delta}\,dQ(c)
\]
로 정의하는 후보를 검토한다. 각 중심을 같은 폭의 균일 대역으로 펼친 혼합이다. 총 광자 수는 \(N_0\), 에너지 평균은 \(m\)를 유지한다.

실제 광자 에너지 분산을 \(W\), 중심 분산을 \(W_c\)라 할 때 독립 균일 변위의 모멘트로
\[
W=W_c+\frac{\delta^2}{3}
\]
를 사용한다. 다음 실행에서 이 관계와 지원구간·양의 밀도·정규화를 먼저 계약으로 확인한다. 중심 분산을 그대로 광자 분산이라 보고하거나, 대역을 원래의 I 밖으로 잘라 내고 정규화 변화를 숨기지 않는다.

평균화 커널 후보는
\[
\bar k_\delta(c)=\frac1{2\delta}
\int_{-\delta}^{\delta}k(c+s)\,ds,\qquad
A_\delta(Q)=\int \bar k_\delta(c)\,dQ(c).
\]
기존 \(k''>0,\ k'''<0\)를 이 평균화에 어떻게 이전할지 직접 논증하고, PHYS26의 증명이 중심 구간·중심 분산에 적용되는 조건을 확인한다. \(\delta=0\) 결과를 유한 폭 결과로 자동 재분류하지 않는다.

초기 기체·serialized numerical J의 정확 실수 해석·source binary64 리터럴·\(qN_0/45\) 정규화와 metric (-+++)·proper seconds·w in eV/H·epsilon² 계수 및 시간 factorial 관례는 그대로 유지한다.

## 4. 목표 결과

이 한 분포족에서 각 허용 \(W\)의 정확한 응답 구간을 구한다. 다음을 함께 처리한다.

- 허용 광자 분산 구간과 그 양 끝점의 분포.
- 극값을 달성하는 중심 측도 및 실제 유한 대역 밀도, 등호 조건.
- 모든 분포가 음수인 구간, 양·음 응답 공존 구간, 모든 분포가 양수인 구간의 경계.
- PHYS26의 델타 허용 경계 \(V_*\simeq16.33994465459\), \(W_0\simeq23.42021899235\ {\rm eV}^2\)와의 정량적 차이.
- 유한 대역족에 대한 결론과 모든 연속 스펙트럼·실제 방출원 admission의 구별.

여러 선폭·여러 평균·여러 초기 기체를 돌리는 phase diagram으로 확장하지 않는다. PHYS26에서 닫은 \(k''\), \(k'''\) 부호와 두 근은 재계산하지 않는다. 새 수치 근이 필요하다면 \(\delta=0.05\)에서 최대 두 개의 새 경계 근만 고려하고, 평균화 적분과 근의 오차를 어떤 수준으로 주장할지 계산 전에 정한다.

## 5. 검증·실행 제한

먼저 이론 경로와 새 수치 경로의 범위·표본·허용오차·예산을 고정한다. 평균화 적분의 서로 다른 적분 경로 또는 충분한 오차 제어가 필요하며, native·gas IVP로 우회하지 않는다. 정확근 정의와 수치 근사·엄밀 구간 인증은 이전 루프와 같이 분리한다. 코드 계보와 원식·상수·J의 공유를 실제대로 기록한다.

PHYS19–26의 main·닫힌 proof suite·기존 근 반복은 0회다. 필요한 순수 helper는 실제 읽은 범위를 기록하고 명시적으로 적응할 수 있다. 생산 source/default/runtime 변경, dense 전 구간 LP 또는 다중 파라미터 campaign은 0으로 둔다. 최초 실패·수정·허용오차 변경을 보존한다.

별도의 실제 final reviewer가 연구 채택을 판정해야 한다. 후보 생성자·검증 설계자가 역할만 바꿔 PROMOTE를 선언하지 않는다. Full-history를 받은 검토자는 NONBLIND다. 재현 replay는 새로 작성한 프로그램에만 제한하고 독립 물리 증거와 합산하지 않는다.

## 6. 완료와 권한

직접 유도, 원 수치·실행 기록, claim DAG, 독립 판정, 재현 묶음, 상태, 단일 후속 질문과 동일 브랜치 additive docs 게시까지 한 루프에서 완료한다. PHYS27 게시 prefix는 다음 실행 날짜의 REI-PHYS27 식별자를 사용한다. 같은 branch 문서 게시 권한을 이어 사용하며 최신 head 확인·nonforce expected-head CAS·source tree 보존을 확인한다. PR merge나 타인에게 메시지 전송은 포함하지 않는다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. 유한 시간·유한 epsilon remainder, J·원자·기체 불확실성, native 동등성, 실제 방출원 admission, 세계 최초성은 승인하지 않는다.
