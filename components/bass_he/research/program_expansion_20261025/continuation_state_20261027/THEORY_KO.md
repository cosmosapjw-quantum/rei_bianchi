# HE-EXP-STATE-04 — 실제 HD 상태 계수와 단일 에너지 소유권

## R1–R3: 질문, 재사용, 입력

EVENT03 source `86306233ce74f5da73b862ec360d5f2ad5c679ca`와 delivery `abf6e277d9a369b5ea412f96d304ff844f32516b`를 이어받는다. 이 단위의 질문은 실제 공개 HD–H+ 상태 전이 계수에서 어떤 population/energy source를 정할 수 있는가이다. 모든 종의 미분 충돌, 각분포와 열화 소유권을 향한 작은 실제 입력 연결이며, 완료된 조건부 2→2 커널을 재실행하지 않는다.

공식 EMAA DOI `10.17178/EMAA_HD_Rovibration_805a7aa5`의 CC BY 4.0 Radex 자료를 고정한다. 원문은 71451 bytes, SHA256 `feda215f1d75ee85de399903c77e18f62c8e323fe709015215634d6ccc7720b6`이다. 52개의 HITRAN Apr2022 준위와 368개의 복사 전이가 있고, H+ 충돌 부분은 19개 상태 사이의 171개 하향 전이, 25개 native 온도, 4275개의 계수이다. 복사와 충돌은 별도 사건이다. 52개의 EMAA local level ID를 WU의 aggregate ID에 자동 결속하지 않는다. 기존 WU reference union104/138/155는 그대로이다.

선택한 edge는 `H+ + HD(v=0,j=1) -> H+ + HD(v=0,j=0)`이다. 원문 upper ID2, lower ID1, 준위 에너지89.227900 및0.000000 cm^-1, weight3 및1이다. Native1005K의 하향 계수는2.48e-10 cm^3/s다. 이 사건은 `H+ + HD -> D+ + H2` 파괴 반응과 다르다. A21=5.443e-8 s^-1은 별도 자발 복사 계수이며 충돌마다 광자를 만드는 규칙이 아니다.

원문 grid의 마지막 온도는3005K이고 논문 서술은3000K까지이다. 원문3005를 보존하되 물리적 support의 결속 전에는 실행 가능한 native selector에서 제외한다. 1005K는 실제 원문 점이며1000K로 이름을 바꾸지 않는다. 보간·외삽·fit 평가를 하지 않는다. SQM 원전 모델과 source precision을 보존하고 근사 오차나 covariance를 새로 추정하지 않는다.

WU HEAD는 단위 직전 `4ea08eb3709c90285946dce2cf824f402056d645`로 갱신되었다. 앞선 f949c21 이후 두 commit/15paths는 R10 전달과 AGENTS 변경이며 reviewed scientific payload34765b943cce5a67d49a622f76c0cf9aeceb635c8cd6a3cf58b5cebb8e3c5fde는 불변이다. 현재 WU priority에서도 EMAA excitation과 reactive destruction을 구분한다. 본 작업은 HE consumer의 새 excitation 입력이며 WU 파일·원장은 수정하지 않는다.

## R4–R5: 상태 차이와 native rate의 연결

준위 파수 \(\tilde\nu_i\)가 cm^-1이면

\[
 \epsilon_i=100hc\tilde\nu_i,\qquad
 \delta=\epsilon_u-\epsilon_l>0.
\]

`c=299792458 m/s`, `h=6.62607015e-34 J s`, `k_B=1.380649e-23 J/K`는 SI 정의상 정확한 상수이다(NIST2022 CODATA SP959). 원전의 인쇄 준위 자체는 무한 정밀 측정값이 아니다. cm^3/s에서m^3/s의 변환은 정확히1e-6이다.

같은 화학 조성의 두 상태를 사용하므로 공통 바닥상태 영점 \(C\)를 더해도 \(\delta\)는 변하지 않는다. 이 population/internal-energy source에는 정밀 HD 관성질량이 필요하지 않다. 원문의 molecular weight3.0을 정밀 동위원소 질량으로 채택하지 않는다. 유한질량 momentum/heat partition은 별도 입력이 생긴 뒤 EVENT03에 결속한다.

Native 하향 계수 \(k_{ul}(T)\)는 원표에서 가져온다. 여기서 thermal bath 가정은 상대 충돌 에너지 분포가 원전 T의 Maxwellian이고 상대 bulk drift가 없다는 뜻이다. 실제 HD/H+ 분포가 이 조건을 만족하는지는 호출자가 결속해야 한다. 이 분포와 microscopic reciprocity, 같은 조성의 공통 비상대론적 관성질량 및 source state-weight 관례 아래에서는

\[
 k_{lu}(T)=\frac{g_u}{g_l}\exp[-\delta/(k_BT)]\,k_{ul}(T).
\]

이 식으로 얻는 상향 계수에는 `derived_by_explicit_thermal_reciprocity` 표식을 붙인다. 새 독립 측정값이나 원문에 인쇄된 상향 행으로 보고하지 않는다. 이 가정을 호출자가 명시하지 않으면 하향 native 값만 제공하고 양방향 source를 실행하지 않는다. 모든 종의 common T/u 또는 LTE population을 자동 가정하지 않는다.

명시적 collider density \(n_p\)와 level densities \(n_l,n_u\)를 입력받아

\[
 j_+=n_p n_l k_{lu},\qquad j_-=n_p n_u k_{ul},\qquad J=j_+-j_-
\]

를 정의한다. 그러면

\[
 \Gamma_u=J,\quad\Gamma_l=-J,\quad\Gamma_p=0,
\qquad \dot U_{\rm int}=\delta J,
\qquad \dot K_{\rm material,total}=-\delta J.
\]

입자수·HD조성·charge는 보존된다. 같은 조성의 상태별 particle count 변화는 총 기체 입자수 변화를 뜻하지 않는다. Population으로 내부 에너지를 구성하므로 \(\dot U_{\rm int}\)는 증거이고 독립 heating RHS에 다시 더하지 않는다. \(\dot K_{\rm material,total}\)은 두 물질의 총 운동에너지 보상량이다. 이 자료만으로 HD와H+ 사이의 partition, 운동량, stress, thermal deposition을 채우지 않는다. 출력의 그러한 필드는 `None/UNASSIGNED`로 남긴다.

명시적 내부상태 population을 진화할 때 그 상태들을 equilibrium partition heat capacity에도 중복 포함하지 않는다. Translational \(C_V\), thermal-particle-count term, explicit internal energy, nonthermal energy는 계속 별도 소유자이다. 방사율 A21은 읽기 전용 source 참고이며 본 collisional adapter에서 실행하지 않는다.

### 평형과 부호 판별

\[
 r_{eq}=\frac{n_u}{n_l}=\frac{g_u}{g_l}e^{-\delta/(k_BT)}
\]

이면 \(J=0\)이다. 같은 bathT에서 \(n_u/n_l<r_{eq}\)이면 내부 에너지가 증가하고 물질 총 운동에너지가 감소하며 반대쪽에서는 부호가 뒤집힌다. 양의 두 flux에서는

\[
 (j_+-j_-)\ln(j_+/j_-)\ge0.
\]

따라서 고정 bathT와 \(n_l+n_u\) 아래에서 \(F=\sum_i n_i\epsilon_i+k_BT\sum_i n_i[\ln(n_i/(g_i n_*))-1]\)에 대해

\[
 \dot F=-k_BT(j_+-j_-)\ln(j_+/j_-)\le0.
\]

이는 이 두 상태·열적 bath 가정의 판별식이며 임의 비열적 분포나 전체 반응망의 인증이 아니다. 영밀도 경계에서는 에너지·count source는 그대로 유효하고, 로그 진단은 극한 또는 미정의 표식을 사용한다. 무한값을 조용히 유한값으로 바꾸지 않는다.

## LiH 원전 교정의 현재 소비자 선택

Bennett et al.2008 erratum DOI10.1111/j.1365-2966.2008.12586.x는2003 spontaneous radiative association rate를 재계산했다. 높은J quasi-bound dipole matrix element 코드 오류를 교정한27행이 현재 HE source selector의 권장 원표이다. 1000K에서17.7→3.19, 3000K에서51.2→1.80이며 단위는1e-20 cm^3/s다. 원래2003표, 기존77 native cells 및 모든 검증 기록은 불변 역사로 보존하고 명시적 supersedes 관계를 추가한다. 같은 사건의2003/2008 계수를 합산하지 않는다. 이 단위는 인쇄 fit을 평가하지 않으며 <7% fit residual을 물리 covariance로 바꾸지 않는다.

Stwalley–Zemke1993 Table2의7LiH X(v0,J0) D0=19589.8±0.3 cm^-1와7LiD의19768.8±0.3 cm^-1는 별개이다. Bennett2003이 권고7LiH D0로 인용한 값은 후자의값과 일치한다. 이 교차원전 isotope 불일치를 기록하고 원저자의 모델 energy나 aggregate branching을 수정하지 않는다. 새 현대 중성 원자 질량과 역사적 질량 관례도 별도로 보존한다. RA branch/광자 에너지로의 수치 결속은 아직 하지 않는다.

## 검증 범위와 다음 의존성

새 source parse/selection/unit conversion/native-pair source를 독립 Decimal80 reference, count·energy 보존, 평형·부호·양성성, source correction selection 및 잘못된 입력으로 검증한다. 정확한 새 input identity에만 검사를 배정한다. 이전 HE101·INTAKE01·DRIFT02·EVENT03·WU suite를 실행하지 않는다. 저장된 새 native points와 원문 LiH표만 plot에 사용하고 plot render에서 과학 함수를 재호출하지 않는다.

유효 결과는 source-bound native thermal internal-state edge와 population-derived energy witness이다. 전체104종의 미분 공급자·질량·각분포·비열적 열화 closure는 남아 있다. 새로운 일반 불가능성 정리나 기존 성과의 최초성 주장은 없다.
