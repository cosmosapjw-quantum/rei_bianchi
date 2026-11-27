# E13C7: 계산 가치에 따른 OFF 전체 경로 정밀화와 병렬 분할

## 판단과 근거 상태

**권고: 짧은 8경로 검증은 현재 환경에서 완결하고, NCP에는 남은 2,331개의 일반 경로만 한 번씩 배정한다.** 이 분할은 서버를 채우기 위해 계산을 늘리는 선택이 아니다. 전회 E13C6 이후 전체 OFF photon enclosure 폭의 98.79391154212048%, heat enclosure 폭의 99.56108697304617%가 바로 이 경로 집합에 남아 있다. 반면 이미 완결된 6경로와 정확히 영인 95경로는 새 적분 대상에서 제외한다. [S1–S4]

이 문서의 상태는 **수학·입력 정적 감사 및 실행 설계 기여**다. 후보 kernel을 실행하거나 수정하지 않았다. 과학 kernel 호출, coefficient evaluation, 기존 과학 계산 재실행은 각각 0이다. CSV 및 저장된 enclosure 폭에 대한 정확 유리수 비교는 수행했으며, 결과와 읽은 bytes/SHA는 `STATIC_OFF_PARTITION_AUDIT.json`에 기록했다. 최종 후보의 독립 decision review를 대신하지 않는다.

수학적 독립성, 기존 조건부 enclosure의 적용 범위, 입력의 exact binary64 해석은 여기서 검토했다. 새 8경로의 실제 N512 성공, N1024의 비용 대비 효과, 새 병렬 실행기 동작, 실제 NCP 성능은 소유자가 새 계약에 따라 얻는 실행 증거로 판정해야 한다. 이 문서 작성 시 이 감사자가 그 결과를 실행하거나 확인한 것은 아니다.

## 1. 실제 입력에 맞춘 작업 분할

원 OFF `SEGMENTS.csv`는 4,884행, `NODES.csv`는 4,880행, `STAGES.csv`는 2행이다. Node는 0–2439의 2,440개이며, 2,436경로는 step 1/segment 0과 step 2/segment 0의 두 구간을 갖는다. 네 경로 0, 700, 1620, 2344는 step 2/segment 1까지 포함한 세 구간이다. [S1]

| 역할 | Node 또는 범위 | 경로 수 | 구간 수 | 권장 처리 |
|---|---|---:|---:|---|
| 이미 채택된 N512 | 0, 700, 101, 102, 410, 413 | 6 | 14 | sealed 결과를 정확히 재사용 |
| 해가 정확히 영인 경로 | 2345–2439 | 95 | 190 | 아래 영해 증명과 저장된 자료 검증으로 유지 |
| 현재 환경의 새 N512 pilot | 105, 106, 409, 414, 1162, 1976, 1620, 2344 | 8 | 18 | 새 과학 계산과 비교를 현재 환경에서 완결 |
| 새 대규모 NCP 작업 | 위 세 집합을 제외한 모든 OFF node | 2,331 | 4,662 | 각 경로를 한 번씩 독립 계산 |
| 합계 | 모든 OFF node | 2,440 | 4,884 | 중복과 누락 없는 분할 |

이 8경로 pilot를 끝내면 NCP 집합에는 event 경로가 남지 않는다. 모든 NCP 경로는 두 구간 모두 source-on이며, 각 경로 내 species mask가 일정하다. HI만 활성인 경로가 691개, HI/HeI가 활성인 경로가 918개, 세 종 모두 활성인 경로가 722개다. 시간·photon·eta·weight seam도 원 binary64 값을 exact lift한 비교에서 모두 일치한다. [S1,S5]

| 새 pilot | 설계 목적 | 실제 captured 구조 |
|---|---|---|
| 105, 106 | 남은 photon 폭 상위 경로 | HI, source-on, 두 구간 |
| 409, 414 | 남은 heat 폭 상위 경로 | HI, source-on, 두 구간 |
| 1162 | 두 종 opacity의 비용·정밀도 대표 | HI/HeI, source-on, 두 구간 |
| 1976 | 세 종 opacity의 비용·정밀도 대표 | HI/HeI/HeII, source-on, 두 구간 |
| 1620 | HeII mask seam과 signed energy anchor 확인 | 세 구간; 마지막 mask가 111→110 |
| 2344 | 초기 영해에서 상단 source-on event로 연결 | 세 구간; source 상태 0→0→1 |

Node 1162와 1976의 일부 구간이 과거 다른 진단에 등장했다는 사실만으로 현재 전체 경로의 N512 결과가 이미 완결됐다고 보지는 않는다. 재사용 단위는 동일한 경로·해상도·정밀도·입력·incoming 정의가 일치하는 sealed 증거여야 한다. 이번 권고는 이미 채택된 전체 경로 6개만 확실하게 제외한다. [S3,S6]

## 2. 95경로의 영해 증명과 절약되는 계산

각 경로의 고정 captured 문제는 구간마다

\[
P'(u)=q(u)-\Lambda(u)P(u),\qquad 0\leq u\leq h,
\]

이며 photon stock은 구간 경계에서 연속으로 전달된다. Node 2345–2439는 첫 초기값이 정확히 0이고, 두 구간 모두 captured `source_on=0` 및 `q=0`이다. 원 coefficient 구현은 source-off일 때 연속 함수 \(q\)를 정확히 영으로 정의한다. 유한한 연속 opacity에 대한 선형 초기값 문제의 유일성으로

\[
P(u)=0
\]

가 첫 구간의 정확한 해다. 다음 초기값도 0이므로 둘째 구간에도 같은 결론이 성립한다. 이 결과는 opacity가 작거나 영이라고 가정하지 않는다. 실제 opacity가 양수여도 homogeneous 방정식은 영해를 보존한다. [S1,S6]

각 흡수 number·energy·heat moment, redshift moment는 \(P\)에 비례하는 적분이므로 모두 0이다. Source number·energy moment는 \(q=0\)이므로 0이다. Signed seam도

\[
J_j=(E_{0,j+1}-E_{h,j})P_j(h_j)=0
\]

이다. 따라서 모든 절대 관측량의 정확한 값은 0이다. 원 captured `n`, `u`, 종별 A/B, `red`, `qn`, `qe`, outflow 및 node 집계도 전부 exact 0으로 확인했으므로 correction 관측량 역시 정확히 0이다. [S1,S5]

정적 감사에서는 이 95경로의 모든 segment 및 node 항을 비교했고 실패가 없었다. 기존 `WIDTH_RANKINGS.csv.gz`의 95×34=3,230행에서 old 및 hybrid 폭이 정확히 0임을 확인했다. 이론 기여자는 기존 전체 `PATHS.jsonl`의 이 95개 절대 endpoint 자체를 다시 읽지는 않았다. 최종 input closure에서 소유자가 원 path 레코드를 읽을 때 각 endpoint의 0도 대조하면 증거 연결이 완성된다. **폭이 0이라는 사실만으로 중심도 0이라고 추정한 것은 아니다.** 정확한 중심 0은 위 영해 증명과 실제 captured 값에서 얻는다.

이 경로들에 N512 coefficient quadrature를 시행하면 190×1,024=194,560회의 coefficient evaluation을 영인 결과를 재확인하는 데 쓰게 된다. 정확 영해 경로로 명시해 제외하는 것이 사용자의 계산 자원 요구에 부합한다. 기존의 유효한 영 enclosure를 retained 항으로 유지하므로 새 근사나 다른 tolerance를 도입하지 않는다.

Node 2344는 이 95개 집합에 포함하면 안 된다. 첫 두 구간은 영해이나 마지막 구간에서 source가 켜진다. 마지막 source-on 구간의 양의 photon 및 moment를 전파해야 하며, 전체 경로를 영으로 처리할 수 없다.

## 3. 일반 경로와 event 경로의 동일 목표 계약

### 3.1 원 숫자의 해석

CSV 문자열은 먼저 binary64로 읽은 값을 정확한 실수로 승격한다. 이것은 CSV의 십진 문자열 자체를 임의 정밀 실수로 해석하는 것과 다르다. \(a,h,E_0,f_0,q_f,\lambda_{if}\), weight, eta, stage old/new 값 및 물리 상수에 같은 규칙을 적용한다. Energy 입력 erg는 binary64 `1.602176634e-12`의 exact lift로 한 번 나눈다. 종별 binding energy와 captured mask cutoff는 서로 다른 상수로 보존한다. [S3,S6]

8종 row 검사를 각각 4,884행에 적용하여 다음을 확인했다: \(a+h=b\), \(0<h<1\), stage 내부 시간 범위, positive weight, 비음수 초기 stock/source/frozen opacity, outflow 0, active heat weight 양수, inactive frozen opacity 정확 0. 실패는 없었다. 2,444 seam에서 time/photon/eta/weight의 exact equality를 각각 확인했고 실패가 없었다. 두 stage의 old/new \(x,y,z\)가 모두 물리적 simplex 안에 있으므로 같은 stage의 선형 보간도 이 domain에 머문다. [S5]

Energy endpoint 검사에는 기존 과학 kernel을 호출하지 않았다. \(0<h<1\)에서 교대급수로 얻는

\[
1-h+\frac{h^2}{2}-\frac{h^3}{6}
\leq e^{-h}\leq
1-h+\frac{h^2}{2}-\frac{h^3}{6}+\frac{h^4}{24}
\]

를 exact Fraction으로 평가했다. \(E(u)=E_0e^{-u}\)가 감소하므로 이 endpoint 하한과 시작 energy로 전체 구간의 source/mask 및 active heat domain을 제한할 수 있다.

### 3.2 자연 threshold와 frozen captured branch를 혼동하지 말 것

일반 NCP 경로 2,331개는 전체 구간에서 자연 cutoff 조건과 captured mask/source 조건이 일치한다. 그러나 event 경로에서는 binary64 event 위치를 exact real로 읽는 과정에서 미세한 차이가 남는다. [S5]

| Captured key | 엄밀한 진단 | 새 결과의 정확한 해석 |
|---|---|---|
| OFF, step 2, node 1620, segment 0 | \(E_h\)가 exact binary64 54.42 cutoff보다 약 \(1.67553556329224\times10^{-15}\) eV 낮지만 HeII mask는 true | 이 구간 전체에서 고정된 captured HeII mask를 사용하는 문제 |
| OFF, step 2, node 2344, segment 1 | \(E_0=100.00000000000004\) eV가 100보다 크지만 source-on | 이 구간 전체에서 고정된 captured source-on을 사용하는 문제 |
| OFF, step 2, node 0, segment 0 | 낮은 source cutoff의 미세한 endpoint 차이 | 전회 채택된 경로의 기존 fixed-source 의미를 유지 |

위 차이는 새 계산의 numerical tolerance로 덮을 대상이 아니다. 원 입력에 이미 들어 있는 frozen branch 목표의 일부다. Source와 mask를 매번 energy에서 재결정하거나 \(E_0\)를 cutoff에 강제로 맞추면 같은 목표를 계산하지 않게 된다. 두 새 event pilot는 **fixed captured branch 조건부 enclosure**로 표시하고, 모든 event에서 natural moving-threshold 문제와 완전히 같다고 주장하지 않는다. 이 차이를 단지 endpoint 하나의 측도 0 문제로 치환하지도 않는다. 시작값이나 끝값의 미세한 차이는 극히 짧지만 양의 길이인 구간에서 threshold 조건을 바꿀 수 있다.

이것이 original fixed-capture 문제의 해를 정밀화하는 데 장애라는 뜻은 아니다. Heat 조건 \(E-\chi_i>0\)는 모든 4,884행에서 엄밀하게 성립하므로 현재 remainder의 positivity 전제와 양립한다. 물리적인 실제 event 시각의 오차를 포함하려면 별도의 target/오차항을 도입해야 한다.

## 4. 완전한 경로를 병렬 작업 단위로 삼는 이유

Gas stage, source, mask를 이미 고정했으므로 서로 다른 node \(n\)의 계수 \(q_n,\Lambda_n\)는 다른 node의 새 photon 해나 moment 합을 읽지 않는다. 이 단계에서 gas를 다시 진화시키는 feedback 연산도 없다. 따라서 전체 한 경로를 계산하는 사상

\[
\mathcal F_n:\;\text{해당 node의 입력 controls, }N,P
\longmapsto \text{해당 node의 enclosure}
\]

은 다른 \(\mathcal F_m\)의 실행 순서와 독립이다. 이것은 계산상의 독립성이지, 확률 변수의 통계적 독립성을 요구하는 주장이 아니다. [S3,S6,S7]

한 경로 **내부**에서는 순서를 바꾸면 안 된다. 다음 incoming correction은

\[
e_{j+1,a}
=[P_j(h_j)-n_{\mathrm{cap},j}]
+[n_{\mathrm{cap},j}-f_{0,j+1}]
\]

이다. `true_minus_captured_interval`에 exact-frozen minus captured 표현 차이가 이미 포함되어 있으므로 이를 다시 더하지 않는다. 둘째 구간을 첫 구간과 별개의 zero-incoming 작업으로 실행하면 다른 문제를 푼다.

Moment correction은 구간에 따라 누적하고 이전 moment의 반경에 다음 photon damping gain을 곱하지 않는다. 이미 흡수된 양과 마지막 photon stock은 다른 상태량이다. Final photon은 마지막 endpoint이며, 중간 endpoint photon을 합산하지 않는다.

Signed energy seam은

\[
\Delta E_j=E_{0,j+1}-E_j(h_j),\qquad
J_j=\Delta E_jP_j(h_j)
\]

이다. 전체 경로의 energy ledger에서는 \(J_j\)를 뺀다. `anchored=false`라는 metadata가 \(J_j=0\)을 뜻하지 않는다. 원 native energy stock과 \(E_hn\)의 표현 잔여도 유지한다. 이 규칙은 ordinary 경로에도 event 경로에도 동일하다. [S3,S6]

기존 `path_enclosure.run_track`은 chronological controls를 순회하여 이 전달을 수행한다. 반면 원 `input_checks`, CLI work-unit 목록 및 `REUSED` 집합은 특정 과거 control을 대상으로 고정되어 있다. 새 dispatcher는 이 고정된 CLI의 node 목록을 억지로 바꾸기보다, 새 manifest/input gate를 가진 wrapper에서 기존 `run_track`과 unchanged kernels를 호출해야 한다. OFF 모드라는 metadata를 KF/GM에 재사용해서는 안 된다. 이번 권고가 OFF 단일 mode에 머무는 것도 target 명료성에 도움이 된다.

## 5. 정확한 최종 reduction과 폭의 의미

각 관측량 \(X\)에 대해 경로 enclosure \(I_{n,X}=[\ell_{n,X},u_{n,X}]\), 원 positive point weight \(w_n\)라 하자. 전체 OFF finite sum은

\[
I_X=\sum_{n=0}^{2439}w_nI_{n,X}
=\left[\sum_nw_n\ell_{n,X},\sum_nw_nu_{n,X}\right]
\]

로 포함된다. 각 경로가 자신의 값을 포함한다면 경로 사이에 어떠한 상관관계가 있어도 이 포함은 유효하다. Fraction으로 저장된 endpoint를 정확히 더하면 더하는 순서는 endpoint 결과에 영향을 주지 않는다. Canonical node 순서를 사용하면 serialization과 SHA도 결정적이 된다.

이 새 분할에서는 전체 budget을

\[
I_X^{\mathrm{new}}=
\sum_{n\in K}I_{n,X}^{\mathrm{sealed}}
+\sum_{n\in Z}[0,0]
+\sum_{n\in L}I_{n,X}^{\mathrm{local}}
+\sum_{n\in B}I_{n,X}^{\mathrm{bulk}}
\]

로 직접 계산한다. 여기서 \(|K|=6,|Z|=95,|L|=8,|B|=2331\)이고 각 항은 이미 정확한 원 weight를 한 번 적용한 값이다. 각 node가 정확히 한 집합에 속하는지를 manifest의 key set으로 검증해야 한다. Old full interval에서 selected interval을 일반 interval subtraction하여 retained sum을 만들어서는 안 된다. [S2,S3,S5]

종별 A/B/H total은 old와 new 양쪽 모두 세 종 interval의 합으로 비교한다. Dedicated total bound를 새 쪽에만 넣으면 계산 방법의 개선과 비교 정의의 변경이 섞인다. Absolute 17개와 correction 17개, 총 34개 항을 같은 규칙으로 보고한다. 이번 정적 감사는 저장된 width CSV에 E13C6 채택 4경로의 새 endpoint 폭을 대입한 뒤 34개 full width가 E13C6의 최신 full budget과 모두 정확히 같음을 확인했다. [S2,S4,S5]

| 현재 E13C6 이후 집합 | 전체 photon 폭 점유율 | 전체 heat 폭 점유율 |
|---|---:|---:|
| 이미 완결된 6경로 | 0.0820356240373% | 0.0233122950591% |
| 정확 영해 95경로 | 0% | 0% |
| 제안된 local 8경로 | 1.1240528338423% | 0.4156007318947% |
| 제안된 bulk 2,331경로 | 98.7939115421205% | 99.5610869730462% |

이 표는 **기존 폭의 위치**다. Bulk 실행 후 이만큼의 폭이 모두 사라진다는 예측은 아니다. 영 폭을 가정한 이론상 최대 가능 폭 감소와 실제 N512의 폭 감소를 구분해야 한다.

## 6. N512·N1024·N2048의 실행 가치 판단

### 6.1 이번 local 진단으로 답할 질문

N512/P60의 8경로 결과를 새 primary local 결과로 먼저 완결한다. 추가 N1024/P60 진단은 105, 409, 1162, 1976을 권한다. 이렇게 하면 photon 우선/heat 우선의 HI 경로와 두 종/세 종 경로의 비용과 반경 구성을 각각 비교할 수 있다. 105와 106만 비교하면 두 종 이상 경로의 비싼 opacity 계산이나 다른 remainder 구조를 대표하지 못한다.

N1024 결과를 본 뒤 bulk 전체를 자동으로 두 배 해상도로 올리는 대신, 각 branch 대표에 대해 다음을 보고하고 원칙을 새 NCP 계약에 고정한다.

1. 두 해상도의 원래 endpoint, overlap, containment, 34개 폭 변화.
2. Numeric/representation, incoming, coefficient-coupling 반경의 절대 크기.
3. 각 경로의 실제 CPU 및 elapsed time, peak RSS, coefficient evaluation 수.
4. 추가 CPU초당 줄인 photon/heat finite-budget 폭.

하나의 물리 tolerance를 새로 발명할 필요는 없다. 이번 단계의 실험 목표를 “같은 captured target의 유효한 finite enclosure를 직접 비교하고, N128 이후 전체 남은 폭에 대한 첫 N512 pass의 성과를 측정한다”로 둔다. 모든 34개 항의 target 일치와 포함 조건을 유지하고, photon/heat 폭 감소를 계산 자원 효율 지표로 사용하면 된다. Source 및 anchor처럼 별도 규모를 가진 항도 기록한다.

N512 primary를 유지할 이유는 전회 4개 HI 경로에서 N128→N512의 selected 폭이 약 13.6–14.6배 줄었고, 이미 동일한 해상도 N128끼리 방법 변경의 이점은 성립하지 않았기 때문이다. 이 사실은 N512가 모든 새 branch에서 같은 배율로 줄어든다는 보장은 아니다. 새 pilot로 직접 검증할 부분이다. [S3,S4]

### 6.2 N^-2 주장을 제한할 이유

원 midpoint certificate의 구간별 quadrature 반경은

\[
R_{\mathrm{quad}}\leq
\sum_{k=0}^{N-1}\frac{hM_k}{24N^3}
\]

이며 \(M_k\)는 whole-cell 두 번째 \(t\)-미분 상계다. 균일하게 제한된 \(M_k\)이면 이 **항**에 대해 \(O(N^{-2})\) 상계를 설명할 수 있다. 그러나 전체 photon/moment 반경에는 coefficient-coupling remainder, 이전 구간 incoming, 표현·방향성 반올림 항도 들어간다. 모든 반경이 동시에 정확히 \(N^{-2}\)로 줄어든다고 할 수 없다. [S3,S6]

N512에서 numeric 항의 비중이 크더라도 그것이 true solution error가 그 크기라는 뜻은 아니다. 반대로 numerical 항이 작아졌다고 analytic floor에 이미 도달했다고 결론 내리지도 않는다. Fixed bound route의 남은 상계는 실제 오차의 양의 하한이 아니다.

N2048은 이 감사의 기본 bulk 권고에 포함하지 않는다. N1024의 추가 비용과 실제 폭 감소가 충분히 유리하고, 그 정보가 다음 판단을 바꾸는 경우에만 소수 경로의 새 work unit으로 계약할 수 있다. 64코어를 쓰기 위해 불필요하게 해상도를 올리는 것은 사용자의 요청과 반대다.

### 6.3 Cost model과 이 문서에서 말할 수 있는 수치

NCP bulk 4,662구간을 모두 fresh local integral로 계산하면 coefficient evaluation 수는 다음과 같다.

| 해상도 | 경로당 coefficient evaluations | 전체 2,331경로 |
|---|---:|---:|
| N512 | 2,048 | 4,773,888 |
| N1024 | 4,096 | 9,547,776 |
| N2048 | 8,192 | 19,095,552 |

여기에는 whole-cell와 midpoint 평가가 각각 N회 포함된다. NCP 주 작업은 저장된 JSON의 재합산이나 25초짜리 4경로 재현이 아니라, 수백만 번의 60자리 directed interval coefficient 평가다.

정밀한 예산은 pilot의 세 branch 비용을 사용하여

\[
\widehat T_{1}\simeq691t_{100}+918t_{110}+722t_{111}
\]

로 세운다. 각 \(t\)는 동일 N/P의 두 구간 경로당 CPU 비용이다. 전회 4개 HI N512 경로의 현재 환경 elapsed 합계 25.253969180994318초를 단순히 4로 나누어 모든 경로에 적용하면 약 4.09시간의 직렬 elapsed라는 **HI 대표 기반 참고값**을 얻는다. 두 종/세 종 비용, I/O와 host 차이를 반영하지 않은 값이므로 확정 NCP wall-time 견적이 아니다. [S4]

새로 발견된 기존 NCP 4경로 return에 유효한 actual elapsed/CPU receipt가 있으면 그 값을 host anchor로 재사용한다. 같은 4경로를 다시 benchmark할 필요가 없다. 현재 환경에서 얻은 두 종/세 종 대비 비용 비율을 보조 자료로 사용할 수 있지만, 64rank 실제 scaling 측정과 구분한다.

## 7. 64코어·128GB를 유용하게 사용하는 실행 형태

소유자가 확인한 현행 HPC 정책은 독립 작업의 OpenMPI 분할, controller를 제외한 N−1 worker 수의 명시, physics 의미 보존, hidden fallback 금지, RAM 20% reserve를 요구한다. 이 문서는 그 정책 파일을 직접 취득한 감사가 아니라 소유자의 정책 확인을 받아 과학 설계에 반영한 것이다. 최종 패키지는 실제 policy bytes와 적용 근거를 포함해야 한다.

권장 형태는 총 64 MPI rank 중 rank 0을 controller/collector로 두고 **63개 worker rank**를 사용하는 것이다. 각 worker는 한 번에 하나의 완전한 경로를 계산하고, Python directed-Decimal kernel은 single-thread로 유지한다. Decimal context와 연산 counter가 process별로 격리되므로 하나의 공유 context에서 여러 thread가 동시에 계산하는 위험을 피할 수 있다.

2331=63×37이지만 경로별 비용은 같지 않다. Node 순서대로 contiguous 영역을 rank에 나누면 species가 많은 영역에 긴 tail이 생길 수 있다. Controller의 dynamic dispatch 또는 branch class를 섞는 결정적 배정이 적절하다. Dynamic dispatch를 써도 최종 결과는 node key에 따라 정렬하며 실행 완료 순서를 numerical identity에 섞지 않는다.

병렬화할 것은 입력이 독립인 **경로 집합**이다. 기존 60자리 directed Decimal arithmetic을 binary64 Fortran으로 바꾸는 것은 전제된 inclusion 증명을 보존하지 않는다. 이번에는 새 물리 hot kernel을 다시 구현하지 않고, 이미 고정된 reference kernel의 작업 배정만 MPI로 바꾼다는 적용 근거를 적는다. 별도 MPFR/interval native backend를 만들려면 방향성 반올림·초월함수 포함·serialization·동일 목표를 새로 검증하는 다른 연구 과제가 된다.

128GB를 가능한 한 가득 채우는 것이 목표가 아니다. 경로당 실측 RSS가 수십 MB인 구조라면 63worker의 순수 worker memory는 수 GB 수준이다. Controller가 전체 2,331개의 상세 결과를 memory에 쌓지 않고 즉시 파일로 수집하면 총 memory 사용도 작게 유지된다. 남은 memory는 OS cache와 변동 여유다. 최소 25.6GB를 reserve하고, observed memory 및 cgroup 한계를 기준으로 worker cap을 계산한다. 단위 GB/GiB는 receipt에서 구별한다.

CPU affinity가 64라고 해서 실제 quota와 물리 코어가 64라고 자동으로 인정하지 않는다. Host preflight에서 affinity, quota, available memory, OpenMPI 버전, Python/Decimal 버전을 기록한다. OpenMPI가 없으면 같은 명령이 몰래 serial 실행으로 바뀌지 않게 명시적으로 중단한다. 별도의 provider attestation이 없으면 `NOT_ASSERTED`를 유지한다.

현재 환경에 실제 OpenMPI가 없더라도 새 branch별 scientific pilot와 process 단위 task isolation은 여기서 검증할 수 있다. 이 근거를 MPI 실행 완료라고 확대하지 않는다. 실제 NCP에서 필요한 preflight, MPI job start와 유용한 bulk scientific tasks만 실행하면 된다. NCP 측 초반 완료 task를 동일 run의 유용한 성능 관측으로 사용할 수 있으며, 별도의 불필요한 scientific warm-up 반복은 넣지 않는다.

## 8. Admission·실패·재개에 필요한 경계

새 패키지는 source kernels, 원 CSV, controls 생성 규칙, retained enclosures, 8개 local primary 결과, bulk key set, N/P와 exact budget reducer를 하나의 입력 closure로 묶어야 한다. 파일명의 `.bin` 유무 같은 전송 이슈는 실행 전에 실제 manifest name와 SHA로 해결한다. 원본 bytes를 바꾸어 통과시키지 않는다.

각 task의 identity에는 mode/node/ordered segment keys/N/P/input hash/source hash를 넣는다. Fresh output reservation 후 시작하고, 완료 결과를 atomic file로 쓰며, host/time/worker 번호는 numerical semantic projection 밖의 receipt로 분리한다. 이미 완료된 task는 identity가 일치하는 증거로 재사용할 수 있다. 미완료 task를 완료됐다고 추정하거나 다른 N/P 결과를 조용히 대입하지 않는다.

첫 worker 실패는 failure receipt와 부분 결과를 보존한다. 이미 완료된 작업을 버리고 전체를 자동 재시도하는 방식은 피한다. 같은 실행이 자동으로 실패 task를 다시 돌리지 않게 하며, 새 resume가 필요하면 원 실패·완료 identity·새 시도 identity를 구별한다. 명시된 최종 key set이 완성되지 않으면 `FULL_BULK_COMPLETE`가 아니다. 부분 결과가 유효하더라도 완전한 전체 N512 결과의 성공을 주장하지 않는다.

서로 다른 결과의 endpoint overlap은 target binding이나 포함 증명의 대체물이 아니다. 과학 admission에는 source/domain/initial/seam 일치, 유한하고 정렬된 intervals, segment 및 stitched ledger의 consistency, old/new 원 endpoint 비교가 함께 필요하다. New interval이 incompatible하면 실패를 보존하고 원인을 찾아야 하며, 임의 tolerance나 hull로 통과시키지 않는다. Intersection을 쓰려면 원래 두 bound와 별도 사전 규칙을 보존한다.

이 설계가 성공해도 범위는 **고정된 OFF captured first-two-step finite enclosure**다. Continuum spectral discretization, 실제 gas trajectory 검증, photon–gas feedback, physical calibration, production 및 receiver adoption은 별도 근거가 필요하다. 현재는 HOLD다.

## 출처와 재현 가능한 정적 근거

아래 source의 실제 bytes/SHA와 전체 exact 결과는 동봉한 `STATIC_OFF_PARTITION_AUDIT.json`의 `read_identities` 및 각 evidence section에 들어 있다. 경로는 이번 환경에서 직접 읽은 위치다.

- **[S1] 원 OFF 입력:** E13C6 package `inputs/source/OFF_SEGMENTS.csv`, `OFF_NODES.csv`, `OFF_STAGES.csv`. SHA 앞부분은 각각 `2a43dae808a0`, `f8c4ce74e4b1`, `d8a363f47781`.
- **[S2] 원 saved budget:** E13C6 intake `returned/BUDGET_EXEC01/BUDGET/WIDTH_RANKINGS.csv.gz`, SHA `23a1cfa6e895474a21d3d71df1ab7589bace5fe4cb6903af3c59d8c94d88ea1d`.
- **[S3] 이전 과학 계약과 이론:** E13C6 `SCIENTIFIC_CONTRACT.md`, `CURRENT_STATE.json`, `theory/TRANSFER_THEORY_KO.md`.
- **[S4] 이전 채택 결과:** E13C6 `ADMITTED_ENCLOSURES.json`, `analysis/NEXT_WIDTH_RANKINGS.json`, `runs/N512_P60/RESULTS.json` 및 기존 E13C6 closeout의 실행 비용. 이 감사의 전체폭 계산은 새 science 실행 없이 [S2]와 `ADMITTED_ENCLOSURES.json`을 사용했다.
- **[S5] 이번 정적 exact 감사:** `/workspace/scratch/7fd51143e473/e13c7_research_20261011/theory/STATIC_OFF_PARTITION_AUDIT.json`, SHA `5e9080f5cd5b0a1a4c2235adecd47704c07571aabfd90a4d4ae3c6f5a0b21ea9`.
- **[S6] 읽은 unchanged kernels:** E13C6 `code/vendor/local_enclosure.py`와 `code/vendor/path_enclosure.py`, SHA `fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370` 및 `c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73`.
- **[S7] 전체 경로 정의:** `e13c6_research_20261011/review/PINNED_PR20_full_first2.py` 및 PR19 lineage `inputs/pr19_lineage/first2/cover.py`.

GPT-6 Astra research harness v4.0.0의 phase 6·7 지침에 따라 정의·전제·유도·실제 정적 검증·앞으로 필요한 실행 증거를 구분했다. 수치 pilot 및 NCP 결과에 대한 최종 review는 이 설계 기여와 독립된 역할에서 수행해야 한다.
