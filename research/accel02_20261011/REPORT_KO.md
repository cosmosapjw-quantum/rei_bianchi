# REI-ACCEL02 — C02B 후속 연구·구현 보고

C02B에서 복원한 완료 RUN002는 다시 계산하거나 검산하지 않았다. N1과 N2를 병렬로 수행하고 BASS N4의 기존 실제 수신 결과를 연결했다. 이번에는 축약 filling-factor 모형을 넘어 **native H/He chemistry·gas temperature·photon field를 z15.9→4, 약1.2713Gyr 동안 실제 적분**했다. 원자율·source·closure·허용오차는 명시한 범위에서 고정했다.

이 보고서의 경로에 남아 있는20261011은 캠페인 식별자다. 실제 실행·Git·백업 receipt의 UTC timestamp는2026-10-10이다.

## 현재 판정

| 항목 | 실제 성과 | 판정 범위 |
|---|---|---|
| N1 | pinned HM12 source와 imported Grackle 저온Case-A H/He/thermal native callsite 연결 | 독립검토 DONE_SCOPED |
| N2 시간·보존 | 실제z15.9→4 native history, late50keV entry 해결, fixed-grid 시간refinement·보존 통과 | 독립검토 DONE_SCOPED |
| N2 스펙트럼·각도 |256×2의 새 전체구간 refinement 실행 | 결과별 최신 판정은 NEXT_DAG.json 및 spectral evidence |
| N4 | BASS PR137의 FLRW/r=+0.1 frozen 수신 결과를 C02B producer에 identity 연결 | 독립검토 DONE_SCOPED, PR140 |
| N3 비등방 새 과학비교 | r0 baseline은 계산됨; r=.05 paired history는 아직 미실행 | spectral/angular gate 전 HOLD |

N4가 수신한 것은 기존 reduced history 두 개다. 이번 새 native H/He history의 BASS 수신 결과로 바꾸어 부르지 않는다. 원래의 CR/RCT 물리 provider와 isotope·확장 원자/핵물리 lane도 완료로 표시하지 않았다.

## 실제 계산한 물리 모형

초기조건은z15.9에서T20K,xHII2e-4,neutralHe이다. 이 선택은 conditional IC이고 HyRec에서 유도된 재결합 history가 아니다. 초기 radiation은 지원 band 안의 HM12 author UVB이고, 이후 RHS에는 현재 stage의 에너지와 redshift로 평가한 author emissivity를 넣는다. UVB를 모든 epoch에 강제하지 않는다.

source의 physical band는10–50000eV이다. 고정 초기 covector grid는 나중에 이 band로 들어오는 ray까지 포함한다. 초기 band 바깥 photon은0이며, source·opacity가 모두0인 dormant mode는 ODE unknown에서 제외해 algebraic zero로 유지한다. 진입 시 exactzero unknown을 추가한다. 음수 state를 clipping하지 않는다.

H/He photoabsorption은 같은 stage의 ion state에 따른 opacity를 사용한다. Grackle Case-A recombination·collisional ionization/excitation·dielectronic recombination·free-free와 signed Compton exchange를 결합한다. CMB는2.7255(1+z)의 prescribed isotropic bath다. source 및 gas·radiation stress의 cosmological backreaction은 풀지 않는다. CR,RCT,secondary cascade,diffuse recombination transport는 포함하지 않는다.

배경은non-tilted axisymmetric dust+Lambda BianchiI의 기존 exact geometry이며, 이번 accepted temporal baseline은r=0이다. redshift는mean-volume scale factor의 역수로 정의한다. 방향별 observed-redshift나 전체 CMB optical depth로 해석하지 않는다. native xHII는 homogeneous ionic fraction으로, 이전 Case-B filling factorQ와 다른 변수다.

## chronology와 보존 문제의 실제 해소

legacy endpoint source injection/full-step newborn absorption은 지속적인 source 생성·흡수와 일치하지 않았다. 고정 covector에서 source를 각 RHS stage에 평가하고, 물리 threshold·source discontinuity·redshift knot를 event 경계로 삼았다. 초기 number-coordinate NATIVE001은 late50keV source-entry에서 적분이 멈췄으며 최초 상태와 exact as-run source를 보존했다.

photon energy coordinate U_j=E_j(t)N_j를 사용하면 다음 식을 얻는다.

$$\dot U_j=E_jS_j-(\kappa_j+\lambda_j)U_j,\qquad \lambda_j=H+s(3\mu_j^2-1).$$

이는 같은 물리 방정식의 좌표 변환이다. photon energy·gas thermal energy·ionization energy와source/escape/work/CMB counter의 전역 ledger가 선형화된다. number ledger는sum(U_j/E_j(t))이므로 별도 오차 판정이 필요하다. energy PASS를 number PASS로 바꾸지 않았다.

| 새 실제 run | 경과시간 | 전구간 | energy 최대오차 | number 최대오차 | 결과 |
|---|---:|---|---:|---:|---|
| NATIVE001 |116.31s|z≈6.04에서 중단|약4.77e-5|별도 보존|최초실패 보존 |
| NATIVE002 |173.53s|15.9→4|6.000e-11|4.548e-8|number FAIL |
| EVENT001 |148.82s|15.9→4|5.32e-11|4.064e-8|number FAIL |
| EVENT002 |306.43s|15.9→4|5.248135677e-11|5.010378246e-10|기존1e-9 bounds PASS |

오차는 energy/initial-energy와number/initial-H-density이다. 최종 판정은 모든 저장 common epoch와 모든 보고된 segment endpoint의 최대값을 합친다. source/work 등의 누적량으로 나눈 보조 metric으로 기준을 바꾸지 않았다. exactzero residual은 그림의 log축에서만 생략하며 원자료는 유지한다.

동일 source·binary·as-run driver·128×2 grid를 사용한 EVENT001/002 비교에서9개 field의 최대 scaled difference는1.423172774e-8이고 고정 기준2e-6을 통과한다. 온도 차이는7.76e-5K 이하, xHII absolute difference는6.65e-10이다. 이는 동일 discretization의 시간refinement evidence이며 절대·continuum error bound는 아니다.

EVENT002의 모든 accepted photon state는nonnegative였고 저장129epoch의 gas domain은 정상이다. 원 run에서 모든 accepted gas state의 domain extrema를 별도 측정하지 않았으므로 그 항목은NOT_EXPLICITLY_MEASURED로 남겼다. 다음 실제256-grid run에는 이 직접 측정·gate를 추가했다. 독립 reviewer는 이 주장 한계를 포함해 시간·보존 범위만 승격했다.

## 물리적으로 해석할 수 있는 새 결과

저장된128-grid 결과는 cold gas의 photoheating·H/He ionization·후기HeIII 증가를 한 coupled history로 제공한다. z4에서xHII≈0.9999948,xHeII≈0.71371,xHeIII≈0.28628,T≈11596K이다. 이는 해당band·IC·closure의 유한-grid 결과이지 관측 우주의 reionization 완료시기 측정값이 아니다.

`figures/NATIVE_GRID_DIAGNOSTIC_128.png`는 실제 저장129epochs로 만든 진단 그림이다. solver를 재실행하지 않았으며 input/output SHA와 plotter를 함께 제공한다. threshold 주변 finite-grid 효과는Gamma curve의 작은 계단 구조에 나타날 수 있다. event 처리는 temporal discontinuity를 정확히 통과하게 하지만 spectral integration error를 제거하지는 않는다.

50keV 위 source energy 누락은z15.9의0.300%에서z4의7.668%로 증가한다. 이 값은 그 자체로 gas-heating 또는 HeII ionization 오차가 아니다. high-energy transport·secondary deposition을 추가해야 영향을 정량화할 수 있다. 이를 이유로 현재 primary lane을 다른물리로 바꾸지 않으며, 동시에 전체HM12 heating 정확도를 주장하지도 않는다.

## 다음 순서와 중단 규칙

1. 실제 EVENT003 결과를 읽고128→256의 같은 전체구간 spectral 차이를 고정1e-3 target에 비교한다. 이미 완료한128-grid 시간검증은 반복하지 않는다.
2. 실패할 경우 어떤field·threshold가 지배하는지 저장history로 특정한 뒤 다음 전체구간 discretization 개선 한 개를 선택한다. 근거 없이512→1024→4096을 자동 반복하지 않는다. 소스나 cross-section을 임의로 smoothing하거나 tolerance를 낮추지 않는다.
3. spectral gate가 닫히면 동일한 조건의r=.05를 최소4angles로 실행하고8angles와 비교한다. 공통mean-z에서Δx,ΔT,ΔGamma를 수치오차와 함께 평가한다. 오차보다 작은 비등방 신호는검출로 부르지 않는다.
4. accepted native history에서proper-time quadrature로ne_eff=(integral ne dt)/Δt를 export하고 새source/run/closure identity로BASS native receiver에 연결한다. 기존 reduced cells를 재명명하지 않는다.

각 단계는 새 이름의 체크포인트, exactsource/input/binary hash, firstfailure, 실제command/exit, independentdecision과 다음action을 남긴다. 현재 RESTART.npz는 상태 evidence이며 지원되는resume CLI가 없다. 다음 실행은 먼저 살아 있는 process와완료RESULT를 확인하고, bare NPZ만으로 이어 실행된다고 가정하지 않는다.

`NEXT_DAG.json`은 low-cost LLM용 node/state/depends/action/criterion을 담는다. `RESUME_PROMPT_KO.md`는 다음 local Codex 시작문이다. 원자율 자체의 개발·재검증, CR/RCT·isotope 확장은별도lane으로 보존한다.

## 게시와 복구

- REI PR110: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/110
- BASS PR140: https://github.com/cosmosapjw-quantum/bass/pull/140
- `publication/BACKUP_RECEIPTS.json`: C02B 복원 및 C03 이후 단계별Drive/Dropbox receipt.
- `review/phase1`, `review/phase2`: 구현/테스트 설계와 분리한 독립판정.

PR은draft이며 merge·owner branch 강제수정은 하지 않았다. 저장·게시 성공은 실제 업로드ack와Git ref/tree identity로 확인했으며, backup identity 확인과 과학검증을 구분했다.
