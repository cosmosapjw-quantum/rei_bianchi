# BASS_HE ENDPOINT14 — 끝점 조건을 유지한 각분포 차수 민감도

## 결과와 수용 범위

**330 MeV에서 양 끝값이 0인 전체 비음수 짝6차 각분포 가족 안에, 고정된 네 EXFOR DCS 민감도 창을 만족하는 함수가 존재한다.** 같은 데이터 창과 끝점 조건에서 QUARTIC12가 인증한 짝4차 가족은 공집합이었다. 이번에는 차수 제한만 확장하여 실제 가능한 다항식을 구성했으므로, 앞선 배제에서 차수 제한이 어떤 역할을 했는지 직접 구별할 수 있다.

새 참조 결과의 수용 결정은 **ACCEPT_SCOPED_ENDPOINT_ZERO_SEXTIC_REFERENCE**다. 단일 실제 campaign의 8개 검증, 별도 코드 경로의 certificate reader, 비저자 과학 심사가 통과했다. Wolfram 평가 1회는 14 literal zero와 16 True를 반환했다. 저장 결과만 읽는 그림 1회도 자원 제한 안에서 완료했다.

이 문서는 과학 결과와 근거를 설명한다. 최종 source·중앙 게시 및 패키지 운송 완료는 별도 최종 권위 문서와 실제 provider 영수증으로 확정한다. R1–R10/C1–C10의 workproduct 수와 과학 DAG의 완료 노드 수는 별도로 관리한다.

## 1. 최신 자료를 조사해 고른 다음 질문

재개 기준은 TANGENT13 S10 commit 049e79cb453b92ac663c4e0a93577a8364c3cf54다. 이번에는 관련 7개 repo의 **1,450 heads를 18개 terminal page까지** 조사했다. 이전 census 대비 신규 6개, 이동 8개, 삭제 0개였다. PR은 state=all로 조회하여 240개 collection record 중 2026-10-22 이후 갱신된 171개를 확인했고, 각 repo에서 날짜 경계보다 오래된 행까지 도달했다. 선별한 PR 13개 section, commit 본문 15개, 과학 source 16개, 현행 AGENTS 2개를 실제 읽었다.

백업·대화 조사 범위는 다음과 같다.

| 자료 | 이번 실제 조사 범위 |
|---|---:|
| Library 최신 변경분 | 62 metadata / 1 terminal page |
| 선택 Library 문서 | 8개 전체 본문 / 10 read windows |
| Dropbox dossier | 5,337 entries / 9 terminal pages |
| Dropbox BASS_BACKUPS | 344 entries / 1 terminal page |
| Drive 문서 변경분 | 1 metadata / 1 terminal page |
| Drive HE archive 폴더 | 1,000 entries, cap 도달 |
| Private context | 실제 1회 SERVICE_ERROR |

Metadata 열거와 본문 읽기는 같은 수준의 근거로 세지 않았다. 이전 완료 조사는 시점이 있는 근거로 재사용했고, 변경분을 단순 합산하지 않았다. Drive 전체와 모든 private chat의 완전 접근은 확보하지 못했다.

새로 확인한 조건부 EOS, thermal jet, CR energy-sum, molecular registry, static-lapse 연구는 각 결과의 입력과 범위에 맞춰 종합했다. 접근한 자료에서 HE의 세 물리 입력을 실제로 닫는 payload는 확인되지 않았다. 한편 QUARTIC12의 최대값과 TANGENT13의 최소값은 이미 완결돼 있었다. 이에 기존 극값을 반복 계산하는 대신, **330 MeV endpoint-zero 배제의 차수 의존성**을 새 질문으로 선택했다.

## 2. 원자료와 모형

반응은 EXFOR M0475002의 **He-4(γ,d)d**, 두 deuteron 채널이다. 새 계산에는 330 MeV의 네 nominal 중심질량 각도와 DCS 창만 사용했다.

| \(\theta_{\rm cm}\) | 고정 DCS 창 (nb/sr) | 고정 증인의 DCS 근삿값 |
|---:|---:|---:|
| 46° | [0.11, 0.17] | 0.169635913719409 |
| 61° | [0.11, 0.21] | 0.118769127531032 |
| 73° | [0.02, 0.12] | 0.118315855717065 |
| 87° | [0.14, 0.24] | 0.140040508293858 |

마지막 열은 표시용 근삿값이다. 실제 창 포함 여부는 nominal cosine의 인증된 구간에서 계산한 exact rational enclosure로 판정했다. ±ERR-S는 결정론적 좌표별 민감도 창이다. 동시 신뢰구간으로 해석하지 않는다. 에너지 격자가 다른 M0475003 총단면적 6점은 결합하거나 보간하지 않았다.

\[
\mu=\cos\theta_{\rm cm},\qquad z=\mu^2,\qquad
f(\mu)=(1-\mu^2)(a_0+a_1\mu^2+a_2\mu^4)
\]

로 놓고,

\[
r(z)=a_0+a_1z+a_2z^2\ge0,\qquad 0\le z\le1
\]

를 요구한다. 계수 \(a_j\)의 단위는 nb/sr이며 음수 계수를 허용한다. 모든 짝6차 다항식 중 양 끝값이 0인 함수는 이 형태로 표현된다. 그 안에서 짝4차 이하인 부분가족은 정확히 \(a_2=0\)이다.

Declared uniform azimuth, 기존 rest energies, target-at-rest kinematic reference와 같은 사건의 검출기 합집합은 유지했다. 새 polynomial degree를 실제 spin·polarization law로 채택하지 않았다.

## 3. 실제 가능한 다항식의 직접 구성

실행 전에 고정한 계수는

\[
(a_0,a_1,a_2)=
\left(\frac{1411}{10000},-\frac14,\frac{33}{25}\right)
\]

다. 이 다항식은

\[
r(z)=
\frac{33}{25}\left(z-\frac{25}{264}\right)^2
+\frac{170627}{1320000}>0
\]

로 정리된다. 따라서 \(f(\mu)\)는 전 구간 \([-1,1]\)에서 비음수이며 \(f(-1)=f(1)=0\)이다. 정규화도 정확히

\[
D=\int_{-1}^{1}f(\mu)\,d\mu
=\frac43a_0+\frac4{15}a_1+\frac4{35}a_2
=\frac{14297}{52500}>0
\]

다.

새 실행에서 이 고정 계수는 네 데이터 창을 모두 통과했다. 결과를 본 뒤 계수를 조정하지 않았다. \(a_2=33/25\ne0\)이므로 이전 endpoint-zero quartic 부분가족 밖에 있다. 이 증인과 이전 공집합 certificate를 함께 쓰면, 같은 데이터·끝점 조건에서 차수 4와 6의 feasibility가 달라진다는 결론을 얻는다.

## 4. 전체 함수족에 대한 엄밀한 경계

계수 영역을 임의로 잘라내지 않기 위해 포함상자를 먼저 증명했다. 46°, 61°, 87°의 세 \(z\) 구간은 서로 \(1/5\) 이상 떨어져 있고 \(z<1/2\)다. 해당 관측 상한과 \(q=(1-z)r\)를 사용하면 세 지점에서 \(0\le r\le1\)이다. 정확한 2차 Lagrange 보간에서

\[
(|a_0|,|a_1|,|a_2|)\le(75,150,75)
\]

가 나오므로 계산의 \(B=160\) 상자는 모든 참 허용계수를 포함한다.

또한 \(|f'|\le18B\)와 87°의 양의 하한을 이용하면

\[
D\ge D_{\min}=\frac{49}{14400000}.
\]

이를 위한 실제 saved-\(\mu\) 주변 구간 포함 검사도 수행했다. 이 하한은 분모 0을 제거하며, 닫히고 유계인 허용집합에서 확률의 최소·최대가 존재하도록 한다.

각 nominal \(z\)의 인증된 구간으로 \((1-z)z^j\)의 중점과 폭을 구하고, 세 signed coefficient의 오차를 모두 포함했다. 관측 창을 수축한 부등식은 충분조건, 확장한 부등식은 필요조건이다.

양성성은 실행 전에 정한 \(N=1,4,16\)에서 다뤘다. 각 cell의 quadratic Bernstein controls가 비음수이면 전 구간 양성인 내부 집합을 얻고, grid node의 비음수 조건은 외부 집합을 준다. 따라서

\[
P_{\rm inner,N}\subseteq T_6\subseteq P_{\rm outer,N}.
\]

각 3차원 polytope의 모든 active constraint triple을 정확한 유리수로 풀고 모든 부등식을 검사했다. 총 24,690개 basis를 열거했다.

| N | Inner 정점 기록 | Outer 정점 기록 | Inner bases | Outer bases |
|---:|---:|---:|---:|---:|
| 1 | 6 | 4 | 680 | 560 |
| 4 | 4 | 4 | 1,771 | 969 |
| 16 | 4 | 4 | 16,215 | 4,495 |

총 26개는 case별 기록의 합인 **inner 14 + outer 12**다. Case를 통틀어 서로 다른 정점 26개라는 뜻은 아니다. N4와 N16의 respective inner·outer 목록은 실제로 같다. 네 nested inclusion도 모두 통과했다.

Reader는 producer를 import하지 않고 저장된 행, 정점, active basis, 증인, 극값, 반올림과 identity를 확인한다. Candidate search와 재열거는 0회다. 정점 목록의 완전성에는 producer의 exhaustive loop, 실제 counts, 유계 polytope 정리가 함께 필요하다. 별도 코드 경로의 reader와 별도 저자가 수행한 과학 심사를 구별해 기록했다.

## 5. 기존 geometry에서 새 weighted moment로

HEMISPHERES는 full-azimuth 실험실 cosine 창 \(A=[0,1]\), \(B=[-1,0]\), CAPS는 \(A=[1/2,1]\), \(B=[-1,-1/2]\)다. 관측량은 같은 사건에서 두 교차 배치 중 하나가 수용되는 합집합의 확률이다.

고정된 330 MeV lab map의 \(K<0\) 단조성을 확인하면 그 사건 집합은

\[
C=[-1,-t]\cup[t,1]
\]

이다. 기존 zeroth monomial moment는 \(k_0=2(1-t)\)이므로, 저장된 경계로부터 \(t\) 구간을 복구할 수 있다. 새 weighted basis에 필요한 적분은

\[
G_j(t)=2\left[
\frac{1-t^{2j+1}}{2j+1}
-\frac{1-t^{2j+3}}{2j+3}
\right],\qquad j=0,1,2.
\]

\(G_j'(t)=-2(1-t^2)t^{2j}\le0\)이므로 \(t\) 구간에서 moment 구간을 얻는다. 같은 threshold로 복원한 기존 monomial 세 성분은 두 geometry 모두 저장값과 정확히 일치했다. Geometry의 형태를 먼저 증명했기 때문에 가능한 재사용이며, 일반 geometry의 zeroth moment 하나로 고차 moment를 추정한 것이 아니다. 기존 preimage·geometry·trigonometry 계산의 재실행은 0회다.

확률은 \(P_g=(k_g\cdot a)/(d\cdot a)\)다. 음수 계수에는 moment 상·하한을 뒤집어 적용한다. 양의 분모를 이용한 가중 convex combination 논증으로, 외부집합의 정점에서 전체 함수족을 감싸는 경계를 얻는다. 실제 내부 증인들이 각 최소·최대의 반대쪽 경계를 제공한다.

## 6. 실제 수용확률 범위

아래는 N16에서 얻은 전체 조건부 함수족의 확률 범위를 포함하는 바깥 방향 12자리 표시다.

| Geometry | 전체 확률 범위의 enclosure | 최소값 bracket | 최대값 bracket |
|---|---|---|---|
| HEMISPHERES | [0.747050288674, 0.783542448014] | [0.747050288674, 0.747050288675] | [0.783542448013, 0.783542448014] |
| CAPS | [0.317079169073, 0.404464291607] | [0.317079169073, 0.317079169074] | [0.404464291606, 0.404464291607] |
| FULL | [1, 1] | [1, 1] | [1, 1] |

N4와 N16의 exact 결과는 같다. HEMISPHERES 최소·최대의 exact bracket 폭은 각각 약 \(7.6967122\times10^{-15}\), \(4.3811398\times10^{-15}\), CAPS는 \(1.4224758\times10^{-14}\), \(1.0097285\times10^{-14}\)다.

N1 CAPS 최대값 bracket은 [0.392235444930, 0.404464291607]로 넓었고, 사전 고정된 N4와 N16에서 좁아졌다. 결과를 보고 추가 mesh를 실행하지 않았다.

전체 range의 폭은 허용되는 각분포 모델에 따른 변화다. 각 최소·최대 주위의 작은 bracket 폭은 계산 certificate의 폭이다. 이 두 폭과 실험적 민감도 창은 서로 다른 양이다.

그림의 왼쪽은 고정된 증인과 네 DCS 창, 오른쪽은 N별 외부 범위와 extrema brackets를 보여준다. 실제 PNG의 오른쪽 상단 legend가 N16 HEMISPHERES 상한 표시의 끝부분과 조금 겹친다. 비저자 심사에서 nonblocking 표시 제약으로 기록했다. 동일 값의 N4 표시와 이 수치표가 읽히며, 정확한 정량 권위는 saved certificate다.

## 7. 실제 검증과 실행 비용

| 항목 | 실제 결과 |
|---|---|
| 새 primary campaign | construction 1회, 8 PASS / 0 FAIL |
| Saved-certificate reader | PASS, 6 polytopes, 26 vertex records |
| Wolfram evaluator | 1회, 14 literal zero + 16 True, warning 없음 |
| Saved-only plot | 1회 PASS, science imports/calls 0 |
| 비저자 실제 결과 심사 | PASS_SCOPED, blocking 0 |

16개 Wolfram True 중 두 개는 단순 부호 control이다. Wolfram의 algebra·candidate 검산을 전체 polytope 열거나 실제 물리법칙 검증으로 확대하지 않았다.

Validation의 whole runner + waited children CPU는 **2.020525 s**, wall은 **1.9446278749965131 s**, max child RSS는 15,752 KiB였다. Plot은 **1.635101 s / 1.5717367499964894 s**, RSS 66,088 KiB였다. 각각 CPU120/wall300, CPU10/wall30 제한과 AS768MiB/thread1을 지켰다. 원격 CAS CPU와 wall은 제공되지 않아 null이다.

실행 pin은 S05 commit **501f4c5a5e5b14b0e05ff5d504578b5b9218caf7**, tree **54bbaf71c917c67f3c5d3b9dcda44e3eecb740c4**다. Source 9개와 입력 2개의 identity를 실제 결속했다. Requested coding model은 gpt-6.1-sol이며 관찰되지 않은 runtime model identity는 null로 남겼다.

실행 전에 빠진 87° 구간 포함 control과 도함수 주석을 수정했다. 모델, 허용오차, 고정 mesh를 바꾸지 않았다. 새 science 실패와 targeted repair는 모두 0회다. S04 Dropbox의 두 FETCH_FAILED는 전송 실패로 보존했고, 같은 봉인 ZIP의 새 파일 전달 참조로 해결했다. 이후 실제 전송 이력은 STAGE_ACKS와 최종 영수증을 따른다.

## 8. DAG와 계속 열린 물리 입력

최종 독립 수용을 반영한 Local 상태는 **14 complete + 1 inherited partial + 3 physical open / 18**이며 중앙은 **28/88, HE delta0**다.

다음 세 묶음은 계속 open이다.

1. EXFOR event/inclusive normalization 및 liquid-He electron/target-motion/response projection.
2. Actual full angular/polarization law 및 photon encounter flux/history.
3. Named nonthermal birth/deposition/thermalization 및 global species binding.

Binding sole owner는 population_rest_energy_witness다. independent_binding_RHS, Gamma_thermal, Cv, species_heating, thermal_deposition은 null, birth_pool은 UNASSIGNED다. global_physical_completion=null, L4=false, production=NOT_APPROVED, activation=false를 유지한다.

TANGENT13·QUARTIC12·EXFOR11·HARMONIC10의 scoped 완료, KINEMATIC08의 inherited partial, PHOTON05의 plot CPU 실패, HARMONIC10의 최초 24 PASS + 1 FAIL 및 targeted 1 PASS, TANGENT13의 runner 실패와 수정 성공을 보존했다. 완료된 science/test/CAS/plot 및 ACK된 백업을 재실행하지 않는다.

## 출처와 최종 권위

- 실제 데이터: [IAEA EXFOR M0475](https://nds.iaea.org/nrdc/exfor-master/entry/m/m0475.txt). 보존 source의 SHA256은 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f다.
- Arends et al., Physics Letters B 62, 411–412 (1976), [DOI 10.1016/0370-2693(76)90671-7](https://doi.org/10.1016/0370-2693(76)90671-7). Publisher metadata와 접근 제한을 확인했다.
- Rice et al., Physical Review C 61, 064612 (2000), [APS abstract](https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612).
- Silverman et al., Physical Review C 29, 35 (1984), [APS abstract](https://journals.aps.org/prc/abstract/10.1103/PhysRevC.29.35).
- Interval polynomial positivity: [Nie–Demmel 저자 공개본](https://mathweb.ucsd.edu/~njw/PUBLICPAPERS/TrnShapOptCoef.pdf), §2. 이번 quadratic 결과는 직접적인 끝점·stationary point 논증으로도 확인했다.

각 원문의 실제 접근 범위는 sources/literature/PRIMARY_SUPPORT_KO.md에 있다. 이 metadata·abstract로 330 MeV의 실제 degree6 각분포 법칙을 확정하지 않는다.

최종 source·central identity와 운송 상태의 권위는 BASS_HE_ENDPOINT14_HANDOFF_KO_20261028.md, BASS_HE_ENDPOINT14_CLOSEOUT_20261028.json, STAGE_ACKS.json, CENTRAL_PUBLICATION_RECEIPT.json, FINAL_DELIVERY_TRANSPORT_RECEIPT.json이다. Git S10/PRE_CAS의 pending은 생성 당시 snapshot으로 보존한다.

