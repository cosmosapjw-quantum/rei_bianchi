# BASS_HE 다음 연구 루프: He 재결합 광자·원자 사건 연결

2026-10-12 · RUX00 입력 재사용 / RUX03 BASS_HE supplier 기여

## 1. 이번 루프의 결론

회수한 물리 입력 중 **warm HM12 extended 이력**을 선택하고, 실제로 사용된 FT03 Case A 원자 사건과 에너지 장부를 고정했다. 그 위에서 재결합의 세 폐쇄—Case A escape, 명시적 광자 수송, 다종 OTS—를 같은 원자핵·전하·에너지 보존식으로 연결했다. 저장된 17개 시점의 RCT 자료는 재사용하고, **He III 복사 재결합과의 경쟁비 17개 및 고정 기체의 단색 광자 응답 6개**를 새로 계산했다.

이번 신규 계산에서
\[
3.0978249002\times10^{-7}\le
\frac{R_{\rm RCT}}{R_{{\rm HeIII},\rm RR}}
\le3.0978393611\times10^{-7}
\]
였다. 이는 선택된 RCT-OFF warm 이력의 저장 시점에서 RCT가 He III RR보다 약 323만 배 작은 사건율임을 뜻한다. 다른 초기 상태·후속 feedback 또는 실제 RCT 방출광의 영향까지 이 비율로 정하지 않는다.

54.42 eV 광자를 초기 기체에 넣고 밀도와 에너지를 고정하면, \(10^{11}\) s 동안의 흡수확률은 처음에 모두 방출할 때 2.1401%, 구간 전체에 균일하게 방출할 때 1.0739%이다. 문턱에서의 광자 적색이동과 기체 변화는 이 작은 응답 계산의 가정 밖이다. 따라서 이 결과는 기존 P03A의 이력 기반 유한 격자 진단과 별도 evidence다.

과학 판정의 정확한 범위와 독립 검토는 review/DECISION.json에 기록한다. 이번 결과는 BASS_HE supplier의 유도·입력 대응·유한 수치 screening이다. rei_bianchi owner의 RUX03 완료에는 실제 RHS의 provider 주입과 해당 실행 증거가 더 필요하다.

## 2. 승계한 출발점과 선택 입력

BASS_HE PR28의 \(354ff664\)에서 B1은 PROMOTE_SCOPED_PYTHON으로 닫혀 있다. 원래 native B1 runtime 및 Python/Rust parity는 해당 이전 상태를 유지한다. E13C11은 PARKED_PENDING_OBSERVABLE_NEED다. 이번 작업은 그 캠페인을 다시 실행하지 않았다.

최신 rei_bianchi PR83의 \(3904f9e2\) 계획을 receiver 계약으로 읽었다. 이 계획에는 세 재결합 폐쇄가 이미 구분되어 있다. 이번 연구는 그 구분을 새 정책으로 발명한 작업이 아니라, 실제 callback과 사건·에너지 식에 연결한 공급자 작업이다.

| 항목 | 이번에 선택한 기존 입력 |
|---|---|
| 계열 | physical_provider_20261010의 extended |
| 광자창 / 격자 | 10–50000 eV / 2904 nodes |
| 저장 이력 | 17 epochs, elapsed 0–\(10^{11}\) s |
| 초기 volume redshift | 5.807 |
| 초기 가스 온도 | 50000 K |
| proper H 원자핵 밀도 | \(5.935621973155476\times10^{-5}\ {\rm cm^{-3}}\) |
| 초기 \(x_{\rm HII}\) | 0.9999754745282792 |
| 초기 \(x_{\rm HeII},x_{\rm HeIII}\) | 0.9700839024387024, 0.029861279382071514 |
| proper 전자 밀도 | \(6.41804549337503\times10^{-5}\ {\rm cm^{-3}}\) |
| 재결합 처리 | 실제 FT03 Case A RR/DR + escape energy |
| 별도 반응 | 기존 이력에서 CR/RCT/HH OFF |

50000 K는 선택된 warm parcel의 입력이며 cold REC 이력 또는 우주 평균 가스 온도로 해석하지 않는다. 기존 base는 10–200 eV, 1984 nodes이고 초기 He III 분율도 다르다. 계산 전에 이 차이를 발견해 extended를 고정했으며 좁은 band 계산은 수행하지 않았다.

HM12 UVB.out는 초기 등방 광자장에만 사용하고 emissivity.out의 comoving emissivity를 각 stage의 E,z에서 별도로 공급하는 기존 규약을 유지한다. 이 둘은 서로 다른 입력이다. 문헌 계보는 Haardt & Madau (2012) 및 저자 배포표를 따른다.[4]

선택된 PR96 warm 실행은 run_interval.py → native main.rs::rhs → ft03_rhs의 경로를 사용한다. native thermal 입력의 photon 값은 [0,0,0]이고, 이후 별도 node별 광이온화와 axisym_coupled_derivative에서 광자·종·에너지를 연결한다. coupled_primary는 함께 존재하는 다른 경로이며 이번 저장 이력의 실행 경로와 구별한다. 원문에 함께 있는 raw Grackle 18개 계수를 warm FT03의 실행 계수로 바꾸어 읽지 않았다. 실제 callback, 단위, 문턱, domain, 폐쇄의 대응은 ATOM_OWNER_MATRIX.json 및 RATE_DOMAIN_MAP.json에 있다.

## 3. 이번에 유도한 물리 연결

### 3.1 같은 사건에서 전자·결합에너지·가열을 함께 계산

HI, HeI, HeII의 이온화 edge 행렬 \(S\)를 고정하면
\[
\mathcal S_{\rm chem}=S(A+C-R_{\rm tot}),\quad LS=0,\quad b^TS=\chi^T
\]
이다. \(L\)은 H 원자핵, He 원자핵, 순전하를 세고, \(b\)는 각 이온의 내부 이온화 에너지다. 이 식으로 원자핵 보존, 자유전자 source, 내부에너지 source가 같은 사건율에서 정해진다.

RCT의 화학량론은
\[
{\rm HI+HeIII\rightarrow HII+HeII+\gamma},\qquad
v_{\rm RCT}=S_H-S_{\rm HeII}=(-1,1,0,1,-1,0)^T.
\]
따라서 직접 자유전자 source는 0이다. 선택된 native 에너지의 차이는
\[
Q=\chi_{\rm HeII}-\chi_H=40.819325400298\ {\rm eV}.
\]
이 Q는 내부에너지 차이며, 실제 RCT 광자의 평균 에너지 또는 spectrum을 제공하지 않는다.

### 3.2 Escape 장부를 광자 source로 옮길 때 지켜야 할 양

FT03의 RR 사건율은 \(R_j=n_en_{j,+}\alpha_j^A(T)\)다. 기존 kinetic cooling이 사용하는 평균 전자 운동에너지는
\[
\epsilon_{{\rm kin},j}=
\frac{k_BT}{\varepsilon_{\rm eV}}
\left(\frac32+\frac{d\ln\alpha_j}{d\ln T}\right).
\]
이에 따른 방출 에너지는 사건당 \(\chi_j+\epsilon_{{\rm kin},j}\)다. 명시적 광자 source \(\eta_j(E)\), photons/(event eV)를 공급할 때는
\[
q_{\rm rec}(E)=\sum_jR_j\eta_j(E),\quad
\int E\eta_j(E)dE=\chi_j+\epsilon_{{\rm kin},j}
\]
를 연결한다. 후식은 기저상태 귀결·별도 반동/잔류 내부에너지 없음의 근사다. cascade multiplicity가 있으면 \(\int\eta_j dE\)는 1보다 클 수 있다.

source에 넣은 에너지 몫을 기존 escape 장부에서 옮겨야 같은 사건의 에너지를 두 번 세지 않는다. 실제 광이온화 사건은 그 에너지를 \(\chi_s\)의 내부에너지와 \(E-\chi_s\)의 열로 나눈다. DR는 resonance별 별도 사건으로 같은 구조를 적용한다. 전체 source를 만들기 전에도 기존 escape energy로 정의되는 양의 측도를 통해 관측량의 조건부 범위를 유도할 수 있다.

### 3.3 Bianchi 특성선 위의 재흡수와 기하학적 일

prescribed 가스·기하 이력의 한 광자에 대해
\[
\dot E=-(H+\sigma_{ab}e^ae^b)E,\quad
\lambda_s=cn_s\sigma_s(E),\quad
\mathcal S(t,b)=\exp[-\int_b^t\Lambda(v)dv]
\]
로 놓으면 종별 흡수확률은 \(P_s=\int\lambda_s\mathcal Sdt\)다. 같은 흡수를 별도 mean-free-path sink로 다시 넣지 않는다. probability와 energy는 각각
\[
\sum_sP_s+P_{\rm out}+P_{\rm surv}=1,
\]
\[
E_b=E_fP_{\rm surv}+\sum_s(\chi_sP_s+K_{{\rm heat},s})
+K_{E,\rm out}+W_{\rm geom}
\]
를 만족한다. \(W_{\rm geom}=\int(H+\sigma_{ab}e^ae^b)E\mathcal Sdt\)는 복사와 기하 사이의 일이며 local heat와 별도다. 상세 유도와 단위 변환은 theory/HE_RECOMBINATION_TRANSFER_KO.md에 있다.

### 3.4 He 광자의 H 재이온화를 포함한 OTS

국소 재흡수 한계에서 \(B_{sj}=\int p_s(E)\eta_j(E)dE\)를 쓰면
\[
\mathcal S_{\rm rec+reabs}=S(B-I)R
\]
이다. 스칼라 Case B는 \(B_{sj}=\delta_{sj}(1-\alpha_j^B/\alpha_j^A)\)의 특별한 대각 근사로 복원된다. He 재결합 광자가 H 또는 다른 He edge를 이온화하면 비대각 항이 필요하다.

다종 coupled OTS에는 Friedrich et al. (2012), §3.1.2의 선행 연구가 있다.[1] 이번 유도는 그 효과를 현재 FT03 사건·에너지 장부 및 Bianchi 응답에 맞춘 것이다. 원자 방출 spectrum의 새 계산이나 coupled OTS의 최초 제안으로 분류하지 않는다.

## 4. 새 수치 결과

### 4.1 저장 warm 이력에서의 RCT–He III RR 경쟁

| 양 | 결과 |
|---|---:|
| 새 RR coefficient/rate 평가 | 저장 시점 17개 |
| 초기 \(\alpha_{{\rm HeIII},A}\) | \(7.321868393221611\times10^{-13}\ {\rm cm^3\,s^{-1}}\) |
| 초기 He III RR 사건율 | \(6.5756246126874794\times10^{-24}\ {\rm cm^{-3}\,s^{-1}}\) |
| 재사용한 초기 RCT 사건율 | \(2.0370228748547873\times10^{-30}\ {\rm cm^{-3}\,s^{-1}}\) |
| 새 \(R_{\rm RCT}/R_{\rm HeIII,RR}\) 범위 | \(3.0978249002\)–\(3.0978393611\times10^{-7}\) |
| 재사용한 PR113 exposure | \(3.4318478685512853\times10^{-15}\) events/H |
| GM25 at 50000 K | 지원 domain 밖으로 거절, 외삽 없음 |

KF96의 선택된 Python scalar provider는 \(10^{-14}\ {\rm cm^3\,s^{-1}}\), 1000–\(10^7\) K를 선언한다. GM25는 200–10000 K다. 지원구간은 provider 계약이며 모든 온도에서의 원자 불확실성 보증은 아니다.

PR113의 17개 시점별 값과 선택된 extended의 t,T,nH,분율이 정확히 일치함을 확인해 이전 RCT rates 및 exposure를 사용했다. 이전 36회 provider campaign은 재실행하지 않았다. exposure는 저장 격자의 piecewise-linear/trapezoid 진단으로, 연속 이력 적분 오차 추정이 없다. 이번 계산에서 실제 KF96 call 1회와 GM25 domain probe 1회만 새로 수행했다.

### 4.2 방출 시각에 따라 달라지는 재흡수 응답

기체와 광자 에너지를 고정하고 \(\tau=\Delta t\sum_scn_s\sigma_s(E)\)라 놓으면
\[
P_{\rm initial}=1-e^{-\tau},\qquad
P_{\rm uniform}=1-\frac{1-e^{-\tau}}{\tau}.
\]
작은 \(\tau\)에서는 \(P_{\rm uniform}=\tau/2-\tau^2/6+\cdots\)다. 따라서 지속 source를 초기 광자처럼 다루면 optically thin 구간의 평균 노출시간을 약 두 배로 잡는다.

| 고정 에너지 (eV) | 처음에 모두 방출: 흡수분율 | 균일 지속 방출: 흡수분율 |
|---:|---:|---:|
| 20 | \(9.64964156\times10^{-6}\) | \(4.82482854\times10^{-6}\) |
| 30 | \(7.19880244\times10^{-6}\) | \(3.59940554\times10^{-6}\) |
| 40.819325400298 | \(3.59629154\times10^{-6}\) | \(1.79814685\times10^{-6}\) |
| 54.42 | \(2.14010593\times10^{-2}\) | \(1.07391108\times10^{-2}\) |
| 60 | \(1.64854185\times10^{-2}\) | \(8.26554531\times10^{-3}\) |
| 100 | \(4.02726565\times10^{-3}\) | \(2.01498713\times10^{-3}\) |

이 여섯 점은 실제 방출 spectrum이 아니다. 40.819325400298 eV는 RCT Q와 비교하기 위한 에너지 표지다. 이 점에서는 흡수 사건 중 HI:HeI 비율이 약 34.96:65.04이고 HeII 단면적은 0이다. 54.42 eV에서는 선택된 기체의 높은 HeII 밀도 때문에 흡수 사건의 99.9915%가 HeII에 속한다. 이는 전체 광자 중 99.9915%가 흡수된다는 뜻이 아니다.

실제 native \(\chi=(13.598434599702,24.587389011,54.41776)\) eV와 Verner fit의 support cutoff \((13.60,24.59,54.42)\) eV를 구별해 사용했다.[3] 특히 54.42 eV 바로 근처에서는 적색이동에 따른 support 이탈을 생략한 frozen response의 한계가 중요하다.

P03A의 기존 2904-node/17-epoch diagnostic은 시간에 따라 달라지는 opacity, 기존 광자 격자 및 segment 왼쪽 끝에 배치한 escape energy를 사용한다. 이번 여섯 에너지는 그 기존 격자의 점과 다르고, uniform birth 응답을 추가했다. 기존 P03A의 cap/retained = 0.011107406480410278 및 cap/min-thermal = \(1.3218886276228445\times10^{-8}\)을 새 계산값으로 세거나 대체하지 않는다.

## 5. 증거와 검증 수준

- **유도:** 사건 행렬, 에너지 장부 이동, Bianchi 한 광자 응답, 다종 OTS 투영, 양의 방출 에너지 측도를 이용한 응답 범위.
- **Symbolic 확인:** Wolfram으로 원자핵/전하 불변식, RCT 전자 source, local energy 합, uniform-birth 장부·급수, 대각 Case B 극한을 확인했다.
- **새 수치 확인:** 17 RR/경쟁비 및 6개 단색 응답. 16개 명명된 check가 통과했다.
- **독립 고정밀 산술 대조:** Decimal80과 binary64를 대조했다. 같은 식의 산술 검산이므로 native code parity나 원자 모형 정확도로 분류하지 않는다.
- **독립 판정:** 후보 생성·검증 설계를 맡지 않은 reviewer가 고정된 문서·source·결과를 읽고 review/DECISION.json을 작성한다.

최대 상대 차이는 RR coefficient \(5.52\times10^{-16}\), 경쟁비 \(6.84\times10^{-16}\), Verner 식 \(2.64\times10^{-15}\), 흡수분율 \(2.16\times10^{-16}\)다. 확률·내부에너지·열·잔존광 에너지 장부의 최대 상대 residual은 \(1.75\times10^{-16}\)보다 작다. 이는 유한 산술 일관성의 증거다.

실제 신규 screening 실행은 그림 생성을 포함해 1.287 s였고 exit code 0이다. 새 ODE 0회, transport 0회, native build 0회, NCP 0회다.

최초 Wolfram 호출의 괄호 syntax 오류와 수정 성공 출력을 모두 보존했다. 입력 선택 전의 base/extended 차이도 기록했다. P03A의 published/executed source 차이는 문서화된 한 docstring 변경을 되돌려 executed SHA를 재구성하고 docstring 제외 AST 동일성을 확인해 해소했다. 이 packaging 해소가 P03A의 물리적 범위를 확대하지는 않는다. P01 fresh native 실행의 source/build binding과 P02A cold 입력 문제는 별도 상태로 남긴다.

## 6. 다음 작업에 넘기는 결정

이번 공급자 산출물은 PHYSICAL_INPUT_ADMISSION.json, ATOM_OWNER_MATRIX.json, RATE_DOMAIN_MAP.json, 유도 노트, screening source/입력/CSV와 독립 판정이다. NEXT_DAG.json은 기존 전체 계획을 보존한 supplier overlay이며 owner의 노드를 임의로 완료시키지 않는다.

다음 최소 행동은 **선택된 warm Case A escape의 사건 bundle을 실제 owner RHS에서 한 번 소비하도록 연결하는 것**이다. 그 작업은 원자 rate·photon absorption·electron source·kinetic cooling·binding·escape energy를 동일 사건과 단위로 연결하고, 실제 사용 source와 실행 binary의 동일성을 먼저 고정해야 한다. 현재 물리 입력이 없다는 이유로 11개 저장 이력이나 B1을 다시 시작할 필요는 없다.

명시적 diffuse photon spectrum 또는 coupled OTS는 관측량에 필요한 \(\eta_j\)나 검증된 응답 모멘트를 정한 다음 별도 branch로 연결한다. RCT total rate만으로 광자 평균 에너지·열 모멘트를 채우지 않는다. RUX02와 RUX03의 독립 supplier 작업 및 receiver preview는 전체 history의 완료를 기다릴 필요 없이 기존 owner 계획대로 이어갈 수 있다.

heavy work unit은 현재 비어 있다. E13C11 precision 작업은 특정 관측량이 필요성을 보일 때 재개한다. 상세 실행 문구는 HANDOFF_KO.md에 있다.

## 7. 파일 안내

- theory/HE_RECOMBINATION_TRANSFER_KO.md: 유도, 가정, 단위, 문헌.
- screening/README_KO.md: 재현 명령, 새 계산과 재사용 구분.
- screening/results/SCREENING_RESULT.json 및 두 CSV: 전체 수치와 check.
- screening/results/FROZEN_ABSORPTION_RESPONSE.png: 방출 시각 및 흡수종 비교.
- PHYSICAL_INPUT_ADMISSION.json / ATOM_OWNER_MATRIX.json / RATE_DOMAIN_MAP.json: receiver 계약.
- SOURCE_AUTHORITY_LOCK.json / RETAINED_RESULTS.json / evidence/: 출처와 계승 상태.
- review/DECISION.json / state/: 독립 판정, 실제 phase 기록, 다음 상태.
- MANIFEST.json: 패키지의 파일별 byte identity.

## 참고 문헌 및 고정 source

[1] Friedrich, Mellema, Iliev & Shapiro (2012), MNRAS 421, 2232–2250, §3.1.1–3.1.2. https://arxiv.org/abs/1201.0602

[2] Hui & Gnedin (1997), MNRAS 292, 27–42, Appendix A. https://arxiv.org/abs/astro-ph/9612232

[3] Verner et al. (1996), ApJ 465, 487. https://arxiv.org/abs/astro-ph/9601009

[4] Haardt & Madau (2012), ApJ 746, 125. https://arxiv.org/abs/1105.2039 ; author tables https://www.ucolick.org/~pmadau/CUBA/DOWNLOADS.html

[5] BASS_HE B1 source: https://github.com/cosmosapjw-quantum/BASS_HE/tree/354ff664c5910d2a17ab3bf0c07ad6ea7e0d4287/research/b1_prescribed_thomson_20261012

[6] Current owner plan: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/3904f9e2791e75db3a3229e5f489bf7d566fe189/docs/fastest_track_chat/REI-ATOMIC-REUSE-RESET-20261012

[7] Retained RCT rate-only source: https://github.com/cosmosapjw-quantum/rei_bianchi/tree/efb63623c4ed0f6c270a677fab3eb0a81ce80e34/research/rct_rate_only_p01_20261011
