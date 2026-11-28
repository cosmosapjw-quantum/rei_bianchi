# BASS_HE EXFOR11 — 실제 EXFOR 자료에 조건부인 동일 사건 수용률

과학 판정: **ACCEPT_SCOPED_DATA_CONDITIONED_APERTURE_REFERENCE**.  
단위: HE-EXP-EXFOR-11 / EXFOR11-DATA-CONDITIONED-APERTURE-REFERENCE.  
S09 채택 후 Local **11 complete + 1 inherited partial + 3 physical open / 15**, Central **28/88, HE delta0**.

이 결과는 공식 EXFOR의 실제 각분포 12점을 사용해, 명시한 양의 짝대칭 다항식족 안에서 두 검출기의 동일 사건 coincidence 수용률을 정확 유리수로 둘러싼다. 원자료에 맞는 하나의 곡선을 임의로 선정하지 않고, 허용되는 가족 전체의 범위를 계산했다. **330 MeV에서 세 가족이 선언한 창과 양립하지 않는다는 결과를 수정 없이 보존했다.**

이 문서는 과학 결과의 S09 스냅샷이다. 전체 R1–R10/C1–C10 및 실제 게시·백업·중앙 전달의 최종 상태는 이후 생성되는 POSTPUBLICATION 외부 인계·closeout·STAGE_ACKS·중앙 receipt가 권위다. Git 내부의 과거 pending을 현재 미완료로 재해석하지 않는다.

## 1. 최신 자료 조사와 선택 이유

접근 가능한 관련 원천의 종료 페이지까지 조사하되, 서비스가 노출하지 않은 범위를 전수 열람했다고 주장하지 않았다.

| 원천 | 확인 범위 | 해석 |
|---|---|---|
| GitHub | owner 51개 repo metadata, 관련 7개 repo 1,432 heads / 18 terminal pages | 이전 1,419 heads 기준 19개 변경·신규 ref; 삭제 0 |
| 변경 ref | 6개 moved compare, 12개 새 non-HE head/filelist와 관련 본문 | 모든 과거 commit 본문 정독을 뜻하지 않음 |
| 최근 파일 | 2026-10-27T00:00 UTC 이후 776개 metadata / 4 terminal pages | 관련 최종 handoff 선택 전문 |
| Dropbox dossier | 5,249 unique entries / 9 terminal pages, 최근 275개 | 해당 dossier subtree 기준 |
| Drive | dossier index 954, 실제 folder 100 children, 최근 관련 62개 metadata | cursor 미노출로 계정 전체 전수 목록 아님 |
| 다른 대화 | 현재 targeted PersonalContext 검색 성공 | 선택 대화 요약; 모든 비공개 대화 전문 접근 아님 |
| 첨부 역사자료 | 20개 파일 identity 및 archive manifest, 관련 본문 | 최신 게시와 역사자료를 구별 |

HE의 마지막 권위는 HARMONIC10 COMPLETE_SCOPED였다. 최신 CR event-union은 전자 marginal과 same-event joint law의 차이를 보존하고 actual exclusive D/C를 공급하지 않는다. WU의 최신 owner loop나 HD 자료 진행, REI thermal C8, REC native-path 복구, BASS lapse/absorption, VigilODE matrix-bound 결과도 각각의 범위를 유지한다. 어느 것도 HE의 실제 핵반응 normalization·광자 history·deposition 입력으로 대체하지 않았다. 중앙의 현재 조사 기준은 df806909aee8f25efcfa4faeefca77a5271f546c이고, 최종 게시 시 별도로 실제 최신 ref를 확인한다.

따라서 새 연구는 또 하나의 manufactured harmonic 확장 대신, **이미 존재하는 실제 DCS 자료가 검출 수용률을 얼마나 제한하는가**를 질문으로 삼았다. 절대 정규화가 열려 있어도 공통 배율이 소거되는 비율에는 구성적인 진행이 가능하다. 상세 출처 종합은 SURVEY_SUMMARY_KO.md, BASELINE_KO.md, sources/R2_PRIMARY_LITERATURE.md에 있다.

## 2. 실제 입력과 문헌 근거

공식 [IAEA-NDS M0475 원문](https://github.com/IAEA-NDS/exfor_master/blob/5392fe533a7230d52147949b59ba8cd9b2f5c081/exforall/M04/M0475.x4)의 SHA-256은 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f이다. M0475002의 각도는 명목 CM 각도 46°, 61°, 73°, 87°다.

| 광자 에너지 MeV | 46° | 61° | 73° | 87° |
|---:|---:|---:|---:|---:|
| 213 | 0.22 ± 0.04 | 0.35 ± 0.09 | 0.41 ± 0.09 | 0.54 ± 0.10 |
| 258 | 0.08 ± 0.03 | 0.23 ± 0.08 | 0.16 ± 0.07 | 0.25 ± 0.07 |
| 330 | 0.14 ± 0.03 | 0.16 ± 0.05 | 0.07 ± 0.05 | 0.19 ± 0.05 |

단위는 nb/sr, ±항은 원문의 ERR-S다. 본 연구는 각 좌표에 \([L_i,U_i]=[\max(0,y_i-s_i),y_i+s_i]\)라는 **결정론적 민감도 창**을 선언한다. 공분산·계통오차·동시 신뢰수준·확률적 독립성을 새로 가정하지 않는다. 명목 각도의 수치 표현 오차는 계산에 포함하지만, 원문에 없는 실험 각도 불확도는 만들지 않는다.

M0475003의 총단면적 6점은 201/225/253/285/320/359 MeV로 별도 보존했다. 각분포의 213/258/330 MeV와 격자가 다르므로 조용히 보간하거나 같은 에너지 제약으로 결합하지 않았다.

[공식 TUNL/Duke Rice1998 학위논문](https://nucldata.tunl.duke.edu/nucldata/Theses/PhD/Rice_1998.pdf) 인쇄 pp.114–115, PDF pp.133–134의 실제 페이지를 확인했다. Eq.5.4는 그 논문에서 동일한 두 deuteron의 사건 총단면적을 \(2\pi A_0\)로 정의한다. 이어 Arends의 총단면적도 0°/180°를 0으로 놓은 Legendre fit에서 얻었다고 기술한다. Rice가 제시한 자체 정의와 Arends에 대한 후속 저자의 설명을 구별한다. Arends1976 DOI 10.1016/0370-2693(76)90671-7 본문의 normalization 식을 직접 확보했다고 주장하지 않는다.

이 자료는 끝점 0이 측정값이 아니라 외삽 가정임을 드러낸다. 그래서 차수 4/8 및 끝점 자유/0이라는 네 가족을 결과를 보기 전에 고정했다. Exa 6회, 요청 후보 합계 35개와 SciSpace 1회·10개 후보를 실제 사용했지만, 최종 근거는 원전과 공식 수치자료다.

## 3. 이론 구성과 정확한 계산

### 3.1 양의 짝대칭 가족

\[
x=(\mu+1)/2,\qquad B_j^n(x)=\binom njx^j(1-x)^{n-j},\qquad m=n/2.
\]

\[
\psi_j=B_j^n+B_{n-j}^n\ (j<m),\quad \psi_m=B_m^n,\qquad
f_a(\mu)=\sum_j a_j\psi_j(\mu),\quad a_j\ge0.
\]

이 가족은 \([-1,1]\)에서 비음수이고 짝대칭이다. 끝점 0의 경우 \(a_0=0\)으로 변수를 제거한다. 이는 양성의 충분한 coefficient cone이며, 모든 양의 다항식을 포괄하는 필요조건으로 주장하지 않는다.

\[
d_j=\int_{-1}^{1}\psi_j\,d\mu=
\begin{cases}
4/(n+1),&j<m,\\
2/(n+1),&j=m.
\end{cases}
\]

정확 유리수 monomial 원시함수를 사용해 적분하므로 수치 quadrature에 기대지 않는다.

### 3.2 명목 각도와 다면체의 안팎 경계

상속한 인증된 삼각함수 구간으로 \(\cos\theta_i\)를 감싸고, 비음수 Bernstein 기저의 interval arithmetic과 \(2^{-60}\) grid의 바깥쪽 반올림을 적용한다. 얻은 벡터를 \(\ell_i\le\psi(\cos\theta_i)\le u_i\)라 하자.

\[
P_{\rm out}=\{a\ge0:\ell_i^\top a\le U_i,\ u_i^\top a\ge L_i\},
\]
\[
P_{\rm in}=\{a\ge0:u_i^\top a\le U_i,\ \ell_i^\top a\ge L_i\}.
\]

비음수 계수 때문에 성분별 bound를 합할 수 있어
\[
P_{\rm in}\subseteq P_{\rm true}\subseteq P_{\rm out}
\]
가 따른다. 측정 각도가 내부에 있어 \(\ell_{ij}>0\)이고 \(a_j\le U_i/\ell_{ij}\)이므로 다면체는 유계다. 양의 \(L_i\)가 영벡터를 배제하고 모든 \(d_j>0\)이므로 \(d^\top a>0\)이다.

r개 변수에서 모든 r개 active constraint 조합을 열거한다. 정확 유리수 선형계를 풀고 singular 조합을 제외한 뒤, 전체 부등식을 만족하는 해만 유지하고 중복을 제거한다. 모든 vertex는 r개의 독립 active constraint를 가지며 유계 비어 있지 않은 다면체는 vertex를 가지므로, 이 유한 열거가 완전하다. 따라서 outer vertex가 없으면 그 고정된 가족/창 조합은 비어 있다. 이는 일반 각분포에 관한 전역 no-go가 아니다.

### 3.3 같은 사건의 유한질량 검출 기하

휴지에너지 \(A=m_\alpha c^2=3727.3794118\) MeV,
\(M=m_dc^2=1875.61294500\) MeV와 실제 에너지를 사용한다. \(c=1\)로 단위를 숨기지 않는다. 상속된 두 딸입자 기하와 정규화된 방위각 \(t=\phi/(2\pi)\)를 재사용한다.

\[
C=(A_+\cap B_-)\cup(A_-\cap B_+).
\]

두 독립 입자의 확률을 곱하지 않는다. 같은 사건의 반대 방향 CM 입자 쌍을 lab frame으로 변환한다. 방위각은 이 연구에서 균일하다고 **선언한 reference**이며 실제 full polarized law를 측정한 것으로 취급하지 않는다.

검출기는 FULL, 서로 반대 반구 HEMISPHERES, lab polar cosine이 각각 \([1/2,1]\), \([-1,-1/2]\)인 CAPS를 사용한다. 새 기하 tolerance는 실행 전에 \(2^{-48}\)로 고정했다. 인증된 \(C^-\subseteq C\subseteq C^+\)에서 기저를 적분하면
\[
0\le c_j^-\le c_j\le c_j^+\le d_j
\]
가 된다.

### 3.4 수용률의 전역 경계

\[
p_C(a)=\frac{c^\top a}{d^\top a}.
\]

\(a=\sum_v\lambda_vv\)인 vertex 분해를 쓰면 이 비율은 vertex 비율들을
\(\lambda_v d^\top v/(d^\top a)\)로 가중한 평균이다. 따라서 최솟값·최댓값은 vertex에서 얻을 수 있다.

\[
\min_{v\in V_{\rm out}}\frac{(c^-)^\top v}{d^\top v}
\le p_C(a)\le
\max_{v\in V_{\rm out}}\frac{(c^+)^\top v}{d^\top v}.
\]

각 끝점의 정확 유리수와 coefficient witness를 저장했다. outer 극값 witness를 실제 명목 fit으로 오인하지 않는다. inner witness는 명목 data window를 만족하지만, 기하값은 여전히 구간이며 실제 전체 가능범위와 동일하다고 주장하지 않는다.

고정 에너지에서 공통 양의 factor \(K(e)\)는 분자·분모에서 소거된다. 각도 의존 표적 응답이나 에너지 적분 안의 상대 가중치는 일반적으로 소거되지 않는다. 실제 사건률·가열을 얻은 것으로 확대하지 않는 이유다.

## 4. 실제 수치 결과

아래 값은 정확 유리수 outer enclosure를 읽기 쉽게 반올림한 표시값이다. 엄밀한 경계와 증인은 evidence/validation/initial/SAVED_PLOT_DATA.json에 있다. 표의 표시 반올림 자체를 엄밀한 바깥쪽 반올림으로 주장하지 않는다.

| MeV | 차수 | 끝점 0 | inner / outer 정점 | HEMISPHERES | CAPS |
|---:|---:|:---:|---:|---:|---:|
| 213 | 4 | 아니오 | 8 / 8 | [0.682624450, 0.766081531] | [0.111219603, 0.288478968] |
| 258 | 4 | 아니오 | 6 / 6 | [0.643711744, 0.729961436] | [0.088483225, 0.248304005] |
| 330 | 4 | 아니오 | 0 / 0 | EMPTY | EMPTY |
| 213 | 4 | 예 | 4 / 4 | [0.682624450, 0.747937605] | [0.111219603, 0.200887823] |
| 258 | 4 | 예 | 4 / 4 | [0.643711744, 0.729961436] | [0.088483225, 0.195637051] |
| 330 | 4 | 예 | 0 / 0 | EMPTY | EMPTY |
| 213 | 8 | 아니오 | 40 / 40 | [0.663652279, 0.789716174] | [0.105261905, 0.417331903] |
| 258 | 8 | 아니오 | 24 / 24 | [0.619914251, 0.752972254] | [0.061331495, 0.300073099] |
| 330 | 8 | 아니오 | 12 / 12 | [0.802883533, 0.843114884] | [0.464673396, 0.569824157] |
| 213 | 8 | 예 | 22 / 22 | [0.663652279, 0.751948654] | [0.105261905, 0.249466439] |
| 258 | 8 | 예 | 17 / 17 | [0.619914251, 0.733714153] | [0.061331495, 0.200458376] |
| 330 | 8 | 예 | 0 / 0 | EMPTY | EMPTY |

FULL은 비어 있지 않은 9개 가족에서 정확히 1이다. 공집합 가족의 수용률은 0이 아닌 null이다.

주목할 점은 두 가지다. 첫째, 213 MeV n=8 CAPS의 상한은 끝점 자유에서 약 0.4173, 끝점 0에서 약 0.2495다. 258 MeV에서도 약 0.3001에서 0.2005로 달라진다. 측정되지 않은 끝점의 가정이 aperture 수용률에 실질적으로 영향을 준다. 둘째, 330 MeV의 degree4 두 가족과 degree8 끝점 0 가족은 outer도 비어 있다. degree8 끝점 자유는 inner witness가 있어 명목 창과 양립 가능함을 구성적으로 보인다. 통과를 위해 차수·오차 배수를 뒤늦게 변경하지 않았다.

## 5. 코딩·검증·독립 심사

실행 소스는 실제 S05 commit fc9fc9c2590ff52af247353c29e04c15162b3ae7, tree ca144ebe6c730a52a5e3e9b375916ac65ce019b5다. 11개 source/dependency 파일과 공식 입력 hash를 pin했다. 작업 디렉터리는 복구한 부분 source mirror이므로 가상의 local D commit을 만들지 않았다.

| 항목 | 실제 결과 | 범위 |
|---|---|---|
| 새 초기 과학 실행 | 1회, 6 PASS / 0 FAIL / 0 error | 12 실제 경우 계산 |
| 저장 certificate reader | 정점 274개 | inner137 + outer137; 전체 부등식·분모·증인 |
| 후보 열거 | RHS별 합계 11,952; singular360; feasible274 | 에너지 간 행렬 역산 재사용 |
| 새 Wolfram evaluator | 1회, literal residual21=0, Boolean8=True | context SERVICE_ERROR와 분리 |
| 그림 생성 | 1회, 과학 import/call0 | 저장 JSON만 사용 |
| 비저자 독립 심사 | PASS_SCOPED | 필수 수정·과학 차단 결함0 |

새 제어는 정확 원문/decimal, Bernstein 성질, 독립 Decimal cosine 포함, constructed inner/outer 다면체, manufactured 기하 적분/물리 경계, 알려진 다면체/비율 극값을 검사한다. certificate reader가 다른 optimizer를 한 번 더 돌린 것으로 횟수를 부풀리지 않는다. 전 정점 목록의 완전성은 유한 열거 알고리즘의 증명과 제어 사례에 근거한다.

| 실행 | 전체 subprocess CPU s | wall s | peak RSS KiB | 계약 |
|---|---:|---:|---:|---|
| Validation | 2.416516 | 2.472070 | 17,200 | CPU60 / wall180 / AS768MiB / 1 thread |
| Saved-only plot | 2.353290 | 2.373904 | 78,536 | CPU10 / wall30 / AS768MiB / 1 thread |

전체 subprocess 측정은 시작·기다린 자식·내부 receipt·종료를 포함한다. 내부 CPU를 다시 더하지 않는다. 모델·provider·최종 외부 metadata serialization까지 포괄하는 총비용으로 주장하지 않는다. Wolfram의 client wall 8.625초는 원격 CPU가 아니며 원격 CPU는 null이다.

요청 implementation executor는 gpt-6.1-sol, 실제 runtime model identity는 미노출로 null이다. Astra root가 계약·수학·최종 채택, lower-tier가 구현·제한 실행, 새 이론/코드를 쓰지 않은 Astra reviewer가 동일한 단일 pass로 source→결과→CAS→실제 PNG를 검토했다. 그림의 공집합 문구 두 곳이 축 테두리에 닿는 미관상 관찰은 해석을 막지 않아 재렌더링하지 않았다.

## 6. 물리적 미완료와 이력 보존

다음 세 입력은 계속 열린다.

1. EXFOR event/inclusive normalization과 액체 He의 전자·표적 운동·응답 projection.
2. 실제 full angular/polarization law와 photon encounter flux/history.
3. 이름이 지정된 nonthermal birth/deposition/thermalization 및 전역 species binding.

Rest/binding의 sole owner는 population_rest_energy_witness다. independent_binding_RHS, Gamma_thermal, Cv, species_heating, thermal_deposition는 null, birth_pool은 UNASSIGNED다. global_physical_completion=null, L4=false, production=NOT_APPROVED, activation=false다.

HARMONIC10의 최초24PASS+1FAIL, targeted1PASS, reserve0을 보존했다. KINEMATIC08 inherited partial과 PHOTON05의 plot CPU 실패도 완료로 바꾸지 않았다. 새 과학/그림은 각 1회 통과했으며 repair 사용0, 남은 실행 reserve는 종료 때0으로 닫는다. 이전에 완료된 science/test/CAS/plot/백업은 재실행하지 않았다.

새 scoped node만 1개 완료해 local11/15로 바뀌었다. 중앙 HE의 물리 완료 기여는0이며 28/88을 유지한다. 모든 전달이 끝나면 다음 명시적 후속 노드가 주어질 때까지 멈춘다.

## 7. 재사용 지도

- CONTRACT.md: 동결된 입력·전제·자원·scope.
- THEORY.md: 원전 입력에서 polytope·ratio certificate까지의 전체 유도.
- src/exfor_aperture.py: 정확 기저·부등식·열거·기하 계수·목적함수.
- tests/test_exfor_aperture.py: 여섯 새 제어 및 저장 certificate reader.
- evidence/validation/initial/: 첫 실제 실행과 정확 유리수 원시 자료.
- CAS_SUBMITTED.wl, evidence/WOLFRAM_RAW.json: 실제 제출·원응답.
- evidence/plot/initial/EXFOR11.png 및 .svg: 저장 자료만으로 생성한 그림.
- review/: 한 번의 비저자 심사의 단계별 기록.
- RESULT.json, DAG.json: scoped admission과 물리적 한계.
- 최종 외부 handoff/closeout/STAGE_ACKS/CENTRAL_PUBLICATION_RECEIPT: 실제 전달 권위. 생성 전 값을 예측해 이 파일에 넣지 않는다.

