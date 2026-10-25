# 독립 C9 실행 심사 — HI_NATIVE_STRAIN_RESPONSE_20261025

## 판정과 다음 행동

**권고: PASS_SCOPED_NATIVE_HI_STRAIN_RESPONSE. Material/blocking finding 0, 필요한 repair 0이다.** Frozen theory/contract의 finite represented HI measure, 명목 M, 초기 isotropic closure, 순간 strain response와 fixed-k mass sensitivity 범위에서 실제 구현·수치 결과를 수용할 근거가 있다. 최종 scientific admission과 publication 결정은 root가 한다.

앞선 R6는 PRE_EXECUTION_REVIEW_KO.md와 REVIEW_PRE.json에 있다. 같은 reviewer /root/next_repo_survey가 actual source/diff/raw를 이어 읽었다. Reviewer는 새 theory/code의 저자가 아니며 독립 심사 역할은 새 단위에 적용된다. Requested/inherited 역할은 Astra scientific reviewer, 실제 runtime model identity는 NOT_EXPOSED다. Review 중 과학 실행·test·CAS·render·기존 계산 재실행은 0이다. 저장된 JSON을 읽고 파일 identity·patch 대응을 확인하는 IO만 수행했다.

## 실제 읽은 구현과 identity

- strain_response.py 전체, SHA256 f65bd3b755a11939ee6801f13dcd7866b12847e242220b671aa5474af26d7a12.
- focused_check.py 전체, SHA256 3dc9badba4346f5647bcb59e7c4932285de2f994f85e84ec44af2bbd7f9d04eb.
- run_focused_once.py 전체, SHA256 ab2ca707d177b09edbaee616fb55f103ec773cf535c6c2236e86e80a35beb5fd.
- PATCH.diff, SHA256 38cd03ccc7bb3102a9af2f253f7fb8e9bf02d0024123437c53a284fdbe6d3225. 다섯 add-only hunk의 실제 added bytes가 해당 source/helper/README와 일치한다.
- PRE_EXECUTION_MANIFEST.json SHA256 31a1a09abfa5cae7ebfabba1fa275831d9536c9ed241817ee074e21478c62f13.
- Root GO의 같은 manifest identity, inputs/INPUT_BINDING.json, README, 실제 raw/stdout.jsonl·stderr·resource_receipt.

새 diff는 allowed leaf에 세 구현 파일, unchanged helper copy, README를 추가한다. 기존 helper를 수정하지 않았다. 실제 W/S 선택은 mass 문자열 510998.95069와 유일하게 일치하는 저장 행이며, prior A/K/L record와 old_moments를 content equality로 묶는다. CSV에서는 redshift=2.479/channel=HI를 선택하고 kinetic_eV·number_weight_per_target_s를 float→exact Fraction으로 읽는다. χ를 다시 빼지 않는다. 새 radial_terms는 R/R_M만 생성하며 old massive_terms 호출은 없다.

## 1. 구현의 식과 interval 정확성

radial_terms의 r,r_M는 R6에서 독립 미분한 식과 일치한다. Coefficients는 saved W/S enclosure에서 C=5W−R, C_M=5S−R_M, κ=2C/15, Γ=C/(3W)를 exact endpoint 연산으로 만든다. Positive denominator 조건과 zero measure의 undefined Γ를 구별한다.

Tensor와 JVP는 C 및 C_M의 exact interval scaling/sum으로 구성된다. Scalar bool·nonfinite·negative amplitude, invalid mass/k/w, 비3×3 또는 비대칭 matrix를 거절한다. B를 자동 symmetrize하지 않는다. 일반적인 큰 cancellation에서는 ROUNDING_UNRESOLVED를 허용하고, 실제 native 출력은 전 성분에서 endpoint certification에 도달했다.

새 native term에는 general Fraction total을 만들지 않고 이미 심사된 dyadic integer accumulator를 그대로 쓴다. Signed R_M에도 floor/ceil enclosure가 적용된다. P128/P160 δ exponent는 R에서 E=−60, R_M에서 E=−79이고 N=4368이다. 실제 raw의 네 grid가 width≤Nδ를 기록하며, 여덟 산출량의 P160⊂P128과 동일 endpoint-rounded binary64가 모두 확인된다.

Native bounds는 단순 float 비교가 아니라 충분조건인 interval endpoint 비교로 검사한다. 예를 들어 R_hi≤β_L²W_lo, C_lo≥(5−β_L²)W_hi, C_hi≤5W_lo를 사용한다. 이는 필요한 관계를 보수적으로 확인한다. L<2M, R_M_hi<0, C_M_lo>0 및 Γ의 [4/3,5/3] 포함도 같은 방식으로 검사됐다.

## 2. Native 실제 결과

아래 값은 raw P160에서 인증된 binary64다. R,C,κ의 단위는 eV target^-1 birth_proper_s^-1, R_M,C_M는 target^-1 birth_proper_s^-1이며 나머지 비율은 무차원이다.

| 양 | 실제 값 |
|---|---:|
| R | 3.2123541371327454e−16 |
| R_M | −6.285950431111738e−22 |
| C | 4.436150261042243e−11 |
| C_M | 1.4143975693305336e−21 |
| κ | 5.91486701472299e−12 |
| Γ | 1.666654597903262 |
| R/W | 3.620629021358712e−5 |
| R/C | 7.241310478915169e−6 |

R/C는 이미 relativistic인 stored W를 유지하면서 C를5W로 근사할 때의 상대 과대평가다. 실제 history나 viscosity coefficient를 새로 추정한 값이 아니다.

B=diag(1,−1,0)의 native strain tensor 대각은
(−5.91486701472299e−12,+5.91486701472299e−12,0)이다.
Synthetic a=2,X=3,da=−1,dX=2,dM=3,dB=diag(0,1,−1)에 대해

Qdiag=(−3.548920208833794e−11,+3.548920208833794e−11,0),

JVPdiag=(−5.914867018117544e−12,−2.95743350702204e−11,+3.548920208833794e−11).

Strain/Q/JVP 3개 tensor의 27개 component 모두 exact interval과 CERTIFIED_BINARY64 status를 보존한다. Trace-free strain에서 native δN와 δK는 exact zero다. Synthetic directions를 실제 cohort 입력으로 바꾸지 않았고 raw에 그 분류가 명시됐다.

## 3. Reference의 실제 독립 범위

Decimal100 reference는 primary의 polynomial rational kernel 또는 enclosure를 호출하지 않고 E=k+M,b=M/E로부터 E(1−b²)²와 (1−b²)[(1−b²)−4Mk/E²]를 적분한다. 입력 atom/M의 identity는 의도적으로 공유한다. Primary와 산술·표현이 다른 numerical reference이며 독립된 물리 모델을 의미하지 않는다.

C/C_M의 Decimal 비교에는 저장된 Decimal W/S를 재사용해 원 적분을 반복하지 않는다. 실제 네 Decimal100 값의 exact-rational 해석점이 P160 enclosure 안에 있고 binary64 대비 상대차는 다음과 같다.

| 양 | 실제 relative difference |
|---|---:|
| R | 4.8089918100344996e−17 |
| R_M | 1.5224649644996653e−17 |
| C | 2.6251064251856207e−17 |
| C_M | 4.054741589888847e−17 |

모두 frozen2e−15 이내다. 원 L0 gate2e−12, precision P128/P160, tolerance 변경0을 유지한다. Decimal containment는 수치 대조이며, enclosure 자체의 증명은 exact term과 directed accumulation/endpoint arithmetic에 있다.

## 4. Controls와 finite transport

실제 raw에서 여덟 control group이 완결됐다. 코드의 require가 어느 하나 실패하면 최종 JSON 출력에 도달하지 않는 구조다.

1. Exact hand R/R_M/C/C_M/κ/Γ.
2. Trace/STF, 선형성, isotropic/shear/offdiagonal tensor와 number/energy literal.
3. 유리수 orthogonal rotation covariance.
4. 전체 amplitude/mass/strain hand JVP literal.
5. Empty/zero, undefined Γ, scalar/matrix/amplitude guards.
6. Exact14 second/fourth moments 및 unreduced tensor identity.
7. Decimal100 finite14 centered convergence와 식(6) remainder.
8. 새 tensor signed cancellation·exact-zero·양/음 underflow·subnormal·unresolved.

Hand JVP는 R6에서 독립 계산한 (−43/5,−8/5,51/5)의 point interval이다. 14-direction fixture는 rational dyad를 저장하며 irrational direction component를 binary64로 반올림하지 않는다. 원 tensor 미분으로 얻은 control은 reduced C expression과 별도로 계산된다.

Finite transport는 실제 exp/sqrt로 transported momentum·energy·volume를 계산한다. 초기 ray measure의 P0=I와 derivative를 사용한 centered error는 다음과 같다.

| h | Frobenius centered error | 직전 대비 |
|---|---:|---:|
| 2^-8 | 1.3740200099867835e−5 | — |
| 2^-9 | 3.4350438564716567e−6 | 0.2499995510621929 |
| 2^-10 | 8.587605785858564e−7 | 0.2499998877650260 |

두 감소율 모두 frozen0.3 이내다. 각 h의 ± endpoint, 총6개 one-sided remainder도 독립 R6에서 확인한 식(6) bound 아래다. 가장 큰 endpoint remainder 약3.091668157717893e−5는 해당 bound3.293573425255335e−4 아래에 있다.

이 비교는 finite14-ray hand measure에 대한 수치 판별이다. 14점 유한 ε 결과를 연속 sphere 전체 적분의 exact값으로 확대하지 않는다. 연속 isotropic native infinitesimal coefficient는 별도 angular identities와 R/R_M 적분으로 정의된다.

## 5. 실제 실행과 자원

- Scientific children1, retry0, exit0.
- CPU0.288967 s = user0.277303 + system0.011664.
- Measured wall0.2912843540107133 s.
- Frozen CPU cap6 s, wall cap8 s; timeout=false, resource_pass=true.
- Peak RSS15104 KiB; launcher address-space cap512 MiB.
- stdout40763 bytes, SHA256 76705beab73674a94cac0813f14ca36999ffe71e2462e87ba31213a29d574e4e.
- stderr0 bytes.
- Resource receipt SHA256 db74effec1c76043127d309dfcbfd009fb793bc6082a2b849408ce1b06f2f82e.

Raw bytes와 receipt identity가 일치하며 GO가 실제 prepared manifest에 결속됐다. Wrapper는 실행 전에 manifest payload identity를 확인하고 exclusive attempt record를 만든다. 코드에는 네트워크 호출이 없다. Thread 환경과 cap이 설정됐고 native math library를 새로 호출하지 않는다.

Known partial before11.160661 s에 현재 child만 더한 부분 합은11.449628 s다. Whole L0는 UNKNOWN_NOT_ZERO, original cumulative cap은 NOT_FROZEN이다. 과거 failed sequence10.110448 s/overrun0.110448 s를 그대로 유지하며 cap reset/relaxation은0이다. Root CAS의 실제 remote CPU, model/IO/packaging 비용은 별도 미측정이며 이 child 비용에0으로 흡수하지 않는다.

## 6. 물리적·수치적 판정의 경계

현재 수용 대상은 represented HI/z2.479의4,368atoms, exact nominalM=510998.95069eV와 명시된 초기 isotropic closure에서의 순간 strain response 및 fixed-k mass sensitivity다. 출력은 source-weighted coeval measure에 대한 birth proper-time당 계수다. 실제 n_HI/time/source/birth history, initial-stock epoch, geometry/frame/clock 및 collision/stopping/heat/photon feedback 입력을 새로 결속한 상태가 아니다.

R6에서 닫은 Frobenius remainder 증명, 이번 code mapping과 실제 discrete fixture가 각각 해당 범위의 근거다. Native finite atomic representation의 exact arithmetic을 원 UV source 또는 cosmological model 전체의 physical-error certificate로 바꾸지 않는다. L4_ready=false, whole_model_completion=null, thermal_heat=null과 기존 owner/예약/실패/예산 기록을 유지한다.

## 종료

현재 한정 theory·implementation·numeric 결과에 대한 독립 review 의무를 닫는다. Scientific source code와 raw를 수정하지 않았다. Material findings0이므로 새 실행·repair·선택적 suite가 필요하지 않다. Root가 이 권고와 actual backup/publication 상태를 연결해 현재 단위를 종료할 수 있다.
