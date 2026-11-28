# HE31 실제 donor on/off 저장 결과 검토

**판정: PASS_SCOPED_PRESCRIBED_DONOR_PAIR.** light_actual_pair_v2의 두 저장 결과, reference_control의 원본 FV 결과, REFERENCE_RECEIVER_PARITY.json, plots/ANALYSIS_SUMMARY.json을 읽고 대조했다. reviewer는 ODE·worker·test suite·benchmark를 새로 실행하지 않았다. prepared evaluator 작성자로서 해당 구현을 독립 승인하지 않으며, 별도 PREPARED_INDEPENDENT_REVIEW의 범위를 유지한다.

## 저장 결과와 요약의 일치

세 파일 모두 payload SHA와 scientific identity hash가 맞고, 현재 frozen receiver implementation identity와 연결된다. 동일한 초기 조건은 Sigma_i=0.003, Pm_i=0.0003, Pr_i=-0.001이다. 각각 40개 물리 상태와 optical-depth 진단 1개, 121 epochs를 저장하며 z=20에서 정확히 z=4까지다. 배열과 history가 유한하고 시간 격자가 증가하며 초기 상태가 같다.

raw state의 shear, gamma/nu quadrupole, elapsed-time, optical-depth와 저장된 H·source constants를 사용해 Sigma와 radiation stress를 다시 표현했다. history의 Pr=Pgamma+Pnu 및 절댓값 norm 표기도 맞는다. endpoint와 on-minus-off는 ANALYSIS_SUMMARY.json과 정확히 일치한다. massive moment를 새로 적분하거나 full Einstein trajectory를 재실행하지 않았다.

| z=4 값 | Thomson off | Thomson on | on − off |
|---|---:|---:|---:|
| Sigma_F | 1.3717105385392087e-4 | 1.3890261117025876e-4 | +1.731557316337896e-6 |
| signed Pm | 1.681387010548691e-5 | 1.6813742618599206e-5 | −1.2748688770511472e-10 |
| signed Pgamma | −1.411516294710385e-4 | −1.365070457928509e-4 | +4.644583678187615e-6 |
| signed Pnu | −9.739524616598499e-5 | −9.739589688549703e-5 | −6.507195120469909e-10 |
| signed Pr | −2.385468756370235e-4 | −2.3390294267834792e-4 | +4.643932958675568e-6 |
| tau_T | 0 | 0.03724155220658596 | +0.03724155220658596 |

이 한 초기 조건에서 photon stress의 크기는 약 3.29049%, radiation 전체 stress의 크기는 약 1.94676% 감소하고 Sigma는 약 1.26233% 증가한다. Pgamma가 처음 음수이므로 양의 delta는 음의 값이 0에 가까워졌다는 뜻이다. matter와 neutrino의 작은 변화는 photon-only 충돌 규약과 모순되지 않는다. 이 성분들은 직접 Thomson을 받지 않지만 공통 Einstein evolution과 H로 정규화한 stress를 통해 간접 영향을 받는다.

off history의 ne_cm3=0은 opacity callback을 비활성화한 진단이다. 같은 donor를 새로운 neutral-gas chemistry로 다시 풀었다는 의미로 읽으면 안 된다.

## 원본 reference 저장 결과와의 비교

reference와 prepared의 실제 donor·초기 조건·nominal numerics가 같고 backend 및 case 이름만 다르다. 저장된 전체 상태 최대 절대차는 1.8030021919912542e-12이며, observable 최대 절대차는 다음과 같다.

| Observable | 최대 절대차 |
|---|---:|
| Sigma_F | 1.585228151003426e-12 |
| Pm | 1.3444106938820255e-16 |
| Pgamma | 9.12545863526737e-16 |
| Pnu | 6.038599524929578e-16 |
| Pr | 1.5163651584382265e-15 |
| tau_T | 1.7347581704463266e-13 |

독립적으로 읽은 saved arrays의 차이가 기존 parity receipt와 정확히 일치하고, 해당 receipt의 절대 기준 1e-10을 만족한다. 이것은 이 저장된 결과에 대한 비교다. prepared 구현 전체의 독립 승인, discretization convergence나 전체 물리 오차 상한으로 확대하지 않는다.

## 해석의 범위

실제 사용한 donor는 R15/HG97-B의 reduced Q history이며 HII=HeII=Q, HeIII=0, residual electron 없음이라는 source closure를 유지한다. 원래 FLRW history를 대상 Bianchi 모형의 mean a에 처방한 계산으로 native H/He chemistry를 다시 푼 결과가 아니다. 현재 광자 모형은 scalar unpolarized Thomson이다.

이번 결과는 한 초기 조건의 z20→4 on/off preliminary sensitivity다. full HE31 parameter sweep, 실제 donor의 z20→2 실행, full polarization이나 새로운 chemistry/mesh convergence는 승인하지 않는다. 기존 D3 z20→2 결과는 별도 단위로 유지한다. 이 한정된 결과 검토에서 unresolved blocker는 없다.
