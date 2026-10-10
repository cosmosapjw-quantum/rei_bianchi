# REI-ACCEL02 C07R — 중단 복구와 전구간 spectral 연구 결과

유실된 256-energy 실행을 실제로 복구했고, **H/He 이온화·기체 온도·광자장을 z=15.9→4, 약 1.2713 Gyr 동안 결합 적분**했다. 에너지·광자수 보존과 직접 측정한 상태 허용 조건은 통과했다. 그러나 128→256 해상도 비교의 최대 차이는 ΓHeI에서 **14.018%**로, 기존 spectral 기준 **0.1%**를 넘는다. 따라서 전구간 실행 능력은 확보했지만 수렴된 재이온화 예측으로 승격하지 않았다.

## 복구 범위와 기존 성과 보존

자동 작업공간 정리로 이전 local-only EVENT_COUPLED003 원자료와 최종 로컬 commit이 유실되어 `RUNTIME_INTERRUPTION_RECOVERY`로 분류했다. 실제 남아 있던 Git head `304afc3592ae60242e3bb72efc56d806519b4a60`와 C06 archive를 복구 기준으로 사용했다. C06 SHA-256은 `c76771b2ce05ff13d9baea2e812f0635a8ba218dc25be27e55fc16127986f560`, 복구 native binary SHA-256은 `3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac`다. 파일·process·하네스 상태는 `recovery/RECOVERY_INVENTORY.json`에 남겼다.

완료된 ACCEL01 RUN002, 128-grid EVENT001/002, 변하지 않은 N1 provider 및 BASS의 기존 수신 검산은 반복하지 않았다. 빠져 있던 256×2, r=0, rtol=1e-11 전체 구간만 새 이름 `EVENT_COUPLED003_RECOVERED`로 계산했다. 이전 대화에만 남아 있던 수치나 final review를 증거로 채택하지 않았다.

| 항목 | 현재 결과 | 범위 |
|---|---|---|
| N1 | DONE_SCOPED 유지 | 실제 source/cold Case-A native provider 연결 |
| N2 시간·보존 | DONE_SCOPED 유지 | 기존 128×2 동일-grid 시간 refinement |
| N2 새 256 실행 | 전구간·보존·상태 조건 통과 | 실제 218개 segment, accepted-state 직접 측정 |
| N2 spectral | FAIL, 수정 경로 준비 | 128×2와 256×2의 경험적 해상도 비교 |
| N3 | HOLD | 새 Bianchi 비등방 paired signal은 아직 미실행 |
| N4 | DONE_SCOPED 유지, BASS PR140 | 이전 reduced FLRW/r=0.1 두 history만 수신 |

새 native H/He history가 BASS에 수신됐다고 주장하지 않는다. 원래 CR/RCT·isotope·확장 핵/원자물리 lane도 별도로 보존한다.

## 물리 계약과 방정식

초기조건은 mean redshift 15.9에서 T=20 K, xHII=2×10⁻⁴, 중성 He다. 이는 conditional IC이며 HyRec 유도 history가 아니다. 초기 광자장은 지원 대역 안의 HM12 author UVB이고, 이후에는 현재 stage의 에너지·redshift에서 author emissivity를 RHS에 평가한다. 각 epoch의 UVB를 강제로 대입하지 않는다.

physical source band는 10–50,000 eV다. 고정 초기 covector q grid는 나중에 50 keV 경계를 넘어 진입하는 광자까지 포함한다. source·opacity·초기장이 모두 영인 dormant mode는 ODE에서 제외해 algebraic zero로 유지하고 진입 시 exact zero 상태를 추가한다. 음수 clipping은 하지 않는다. Case-A escaped radiation, Grackle RR/CI/DR/CE/free-free, signed Compton exchange를 유지한다. CMB는 T_CMB=2.7255(1+z)의 prescribed isotropic bath다.

배경은 기존 non-tilted axisymmetric dust+Λ Bianchi I test-field geometry이며 이번 실행은 r=0이다. CR, RCT, secondary cascade, diffuse recombination 재흡수, gas/radiation stress backreaction은 포함하지 않는다. mean-volume redshift는 방향별 observed redshift가 아니며, homogeneous ionic fraction xHII는 이전 filling factor Q와 다르다.

고정 q의 실제 에너지를 E_j(t), reference-volume photon number를 N_j라 하면 U_j=E_jN_j를 적분한다.

$$\dot U_j=E_j S_j-(\kappa_j+\lambda_j)U_j,\qquad
\lambda_j=H+s(3\mu_j^2-1).$$

이 변수는 동일한 물리계의 에너지 ledger를 선형화한다. photon number는 Σ_j U_j/E_j이므로 별도 보존 판정이 필요하다. energy PASS가 number PASS 또는 spectral PASS를 뜻하지 않는다. source-entry event 처리로 chronology 문제를 해결했어도 spectral 적분 오차는 남는다.

## 실제 새 실행 결과

| 측정량 | EVENT_COUPLED003_RECOVERED |
|---|---:|
| 구간 | z=15.9→4, 4.0119269418×10¹⁶ s |
| grid | 256 energy × 2 angle, FLRW r=0 |
| 실행 시간 | 629.20 s |
| RHS / Jacobian 호출 | 216,967 / 1,869 |
| 완료 segment / 저장 epoch | 218 / 129 |
| 최대 energy/initial-energy residual | 6.6493278602×10⁻¹¹ |
| 최대 photon-number/initial-H residual | 5.5014857431×10⁻¹⁰ |
| 각 ledger의 기존 허용 기준 | 1×10⁻⁹ |
| accepted finite/gas-domain/photon positivity | 모두 실제 측정 통과 |

ledger 최대값은 보고된 segment endpoint와 저장된 공통 output epoch를 합친 값이다. 모든 연속 시각에 대한 수학적 bound는 아니다. accepted gas의 T 범위는 약 20–12,355.80 K, xHII 범위는 약 0.0002–0.99999478이며, 이온분율·EOS·finite 조건을 직접 측정했다. 기존 EVENT002의 모든 accepted gas state는 별도 측정하지 않았으므로 그 항목은 계속 `NOT_EXPLICITLY_MEASURED`다.

기존 128×2 시간 refinement의 최대 scaled field 차이는 1.4231727742×10⁻⁸로 기준 2×10⁻⁶을 통과한다. 기존 energy/number 최대 residual은 각각 5.2481356770×10⁻¹¹, 5.0103782457×10⁻¹⁰이다. 이 scoped 판정을 재사용했으며, 이를 256-grid 자체의 별도 시간 refinement 판정으로 복사하지 않았다.

## 해상도 비교와 남은 blocker

`EVENT_SPECTRAL_COMPARISON_RECOVERED.json`은 같은 실제 epoch에서 128과 256의 차이를 fine history의 해당 field 최대 진폭으로 정상화한다. 129-epoch와 65-epoch subset은 각각 자신의 표본 집합으로 정상화하며 섞지 않는다. 원 N2 frozen-bath 계약은 65 epoch와 number ledger 10⁻¹⁰을 썼고, 결합 native 계약은 129 output epoch와 number ledger 10⁻⁹을 명시한다. 각 계약을 유지했다.

다음은 129-epoch 비교다. 표의 값은 grid 간 차이이지 정확해에 대한 인증 오차가 아니다.

| field 또는 moment | 최대 정상화 차이 | 10⁻³ 기준 |
|---|---:|---|
| xHII | 0.00179100 | FAIL |
| xHeII | 0.00259590 | FAIL |
| xHeIII | 0.00677235 | FAIL |
| T | 0.00413458; 최대 절대 차이 51.03 K | FAIL |
| ΓHI | 0.12691813 | FAIL |
| ΓHeI | 0.14018076 | FAIL |
| ΓHeII | 0.06315329 | FAIL |
| 순간 source photon number, reference volume | 0.11504560 | FAIL |
| 순간 source energy, reference volume | 0.08630366 | FAIL |
| 총 proper photoheating | 0.01632884 | FAIL |

총 24개 field/moment 중 23개가 기준을 넘는다. 65-epoch 검사도 FAIL이며 최대값은 동일한 ΓHeI의 0.14018076이다. 종별 photoheating·source·radiation energy moments는 저장된 실제 state와 같은 pinned source/native cross-section으로 복구했다. 이는 원 N2가 명시한 source/heat 의무를 추적하는 자료이며, 원 frozen-bath 결과를 새 native 검증으로 대체한 것이 아니다.

에너지대역별 저장값 분석에서는 ΓHI의 차이가 13.6–24.59 eV, ΓHeI는 24.59–54.42 eV, 순간 source number는 10–13.6 eV에서 주로 나타났다. 근거는 `n2/evidence/SPECTRAL_BAND_LOCALIZATION_RECOVERED.json`에 있다. 순간 source moments 자체에서도 차이가 크므로 source quadrature와 photon-state/threshold response를 분리해 볼 근거가 생겼다. 하지만 source table, threshold, quadrature 중 하나가 유일한 원인이라고 확정하지 않는다. local RHS ledger가 작다는 사실만으로 각 적분항의 연속 스펙트럼 정확도를 보장할 수 없다.

`figures/NATIVE_SPECTRAL_RECOVERED_128_256.png`와 SVG는 실제 저장값으로 만든 진단 그림이다. 실선은 128, 파선은 256이며, 오른쪽 아래에는 9개 native field의 129-epoch 오차를 표시했다. 전체 24개 moment/field의 판정은 JSON 및 독립 review를 따른다. 그림 생성은 ODE를 호출하지 않았고, 기존 128 그림은 수정하지 않았다. 원자료·plotter·출력 hash는 `SPECTRAL_RECOVERED_FIGURE_PROVENANCE.json`에 있다.

50 keV 위의 원 HM12 source energy 누락은 z15.9의 0.300%에서 z4의 7.668%로 증가한다. 이를 곧바로 gas heating 또는 HeII ionization의 오차로 해석할 수 없다. 현재 결과는 고정 band·conditional IC·선택된 closure의 진단이며, continuum 수렴이나 관측적 재이온화 예측을 주장하지 않는다.

## 추가 Q0 연구: source와 초기 UVB 오차의 분리

`recovery/Q0_SOURCE_ATTRIBUTION.md/.json`에서 source와 초기 radiation의 quadrature 오차를 추가 ODE·native RHS·SIGMA 호출 없이 계산했다. 기준은 pinned HM12의 **선언된 piecewise interpolation에 대한 해석적 moment**이며, 실제 물리적 연속 스펙트럼에 대한 정확해는 아니다. source profile은 exact-reference history 진폭으로 정상화한 원인분해 진단이다. 공식 128/256 spectral 판정의 fine-grid 진폭 정상화와 별개이며, 새 허용 기준으로 바꾸지 않았다.

| full-band source 진단 | 128 grid | 256 grid |
|---|---:|---:|
| reference-volume photon number 최대 정상화 오차 | 10.31555% | 5.08064% |
| reference-volume energy 최대 정상화 오차 | 7.89482% | 3.96376% |

이 source-only 오차는 gas feedback과 무관하게 직접 확인됐다. 초기 UVB의 full-band photon number signed error는 128에서 +0.08133%, 256에서 +17.32147%로 비단조적이다. HI-ionizing photon number는 −4.88387%/−0.35907%, HeI-ionizing number는 −9.61879%/−2.62002%다. 두 grid는 동일한 물리적 IC 처방을 사용하지만, 그 처방을 적분한 discrete 초기 photon number/energy가 같다는 뜻은 아니다. 독립 band 분해에서 256-grid full-number 오차의 거의 전부는 HI threshold 아래 10–13.6 eV에 있다. 따라서 +17.32147%를 ionizing-photon 또는 gas-heating의 17.3% 오차로 부르지 않는다. 초기 total photon number, ionizing 부분집합, 이후 Γ·heat는 서로 다른 moment이므로 이 수치들을 하나의 물리 오차로 합치지 않는다. 균등 grid 증설만으로 모든 초기/source 적분이 단조 수렴한다는 가정도 하지 않는다.

Q0 계산과 제한된 독립 검토가 완료됐다. `review/recovery/Q0_DECISION.json`의 판정은 `ACCEPT_SOURCE_AND_INITIAL_FIELD_QUADRATURE_ATTRIBUTION_ONLY`이며, SHA-256은 `962c9979e759746e0145b23429312ec443e74e74eabbe8924949ba1d28e1511b`다. reviewer는 원 table을 별도 파싱해 초기 8개 moment와 4개 epoch의 source 32개 moment를 독립 적분했다. 최대 상대차이는 각각 3.396×10⁻¹⁵와 7.803×10⁻¹⁶이다. 129개 source epoch 모두를 독립 재적분한 검토는 아니다. evolved Γ·T·ion fraction의 전체 오차를 source, 초기장, opacity quadrature, 비선형 feedback 사이에 완전히 배분한 것은 아니다. 다음 후보의 사전 knot는 초기 UVB jump와 source/threshold 궤적을 함께 고려해야 한다.

## 다음 연구 루프: 원인 분해 후 한 개의 보존적 수정

`recovery/QUADRATURE_NEXT_STEP.md/.json`의 실제 코드 조사에 따라 다음 순서를 정했다.

1. **Q0 — source/IC 원인 분해 완료.** 위 실제 attribution 결과와 독립 검토를 재사용한다. 같은 후처리나 완료된 ODE를 반복하지 않는다.
2. **Q1A — 최소 변경 후보.** q와 양의 weight를 실행 전체에서 고정한 composite Gauss grid를 설계한다. 초기 UVB jump 및 source/threshold 궤적을 참고해 사전 knot를 배치하고 기존 native RHS·counter·Jacobian을 그대로 사용한다. 매 시각 threshold에 정확히 정렬되는 방법은 아니며, 개선 여부는 새 전구간 비교 전까지 미확정이다.
3. **Q1B — 필요한 경우의 별도 대안.** 고정 q-cell의 N과 Q=∫q dN 두 모멘트, 양의 realizable reconstruction, 공통 absorption/source/heat 적분을 도입한다. 이는 새 수치 closure·Jacobian 검증이 필요한 더 큰 작업이다. 현재 packet 식에 움직이는 q/weight만 넣거나 한 packet에 서로 맞지 않는 source number/energy moment를 강제하지 않는다.
4. **Q2 — 선택한 한 경로의 장기 실행.** 동일한 z15.9→4 전체 구간에서 candidate/enriched pair를 비교한다. source·원자율·IC·물리 band·기존 tolerance는 유지한다. Γ·heat의 사후 보정이나 counter만의 수정은 허용하지 않는다. 새로운 discretization의 시간·ledger·domain 근거도 확보한다.
5. **Q3 — 승인된 후속 과학 비교.** spectral 기준을 통과한 뒤 r=0 대 r=0.05, 최소 4/8 angle의 실제 Bianchi 비교를 수행한다. 공통 mean-z에서 Δx, ΔT, ΔΓ를 수치오차와 비교하고 오차보다 작은 효과는 검출로 부르지 않는다.

무제한 512→1024→4096 균등 doubling이나 인접한 좁은 redshift 구간 검사를 기본 경로로 삼지 않는다. 바뀌지 않은 실패를 다시 실행하거나 허용 기준을 낮추지 않는다.

병렬로 가능한 일은 세 가지다. 실제 `--resume` CLI의 source/active-event/state identity 검증, Q0 결과를 활용한 source/serialization profiling, 새 native history용 BASS schema와 producer quadrature 계약이다. 현재 `RESTART.npz`에는 상태가 있지만 지원되는 resume CLI는 없다. 완료된 run을 재실행해 이를 대신하지 않는다.

새 native history가 수용되면 proper-time cell의 ne_eff=(∫ne dt)/Δt를 실제 producer quadrature와 함께 export하고 새 run/source/closure/units/frame identity로 BASS에 연결한다. N4의 기존 reduced cell을 재명명하지 않는다. observer tail이나 null-covector endpoint inversion 없이 total CMB τ 또는 fixed-observed-z 방향별 τ를 주장하지 않는다.

## 독립 판정, 게시 및 복구 자료

기존 scoped acceptance는 `review/phase1`과 `review/phase2`에 보존했다. 이번 복구 경계 및 실제 새 수치의 독립 판정은 `review/recovery/`에 분리했다. `SPECTRAL_DECISION.json`의 판정은 `PROMOTE_SCOPED_RECOVERED_RUN_CONSERVATION_AND_DOMAIN_HOLD_SPECTRAL_ADMISSION`이다. reviewer는 65/129 두 집합의 48개 metric을 저장값에서 독립 재계산했고, 보존·domain만 수용하며 spectral 실패를 유지했다. 구현자·후처리 담당자가 단독으로 spectral 완료를 승격하지 않는다.

- REI: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/110
- BASS: https://github.com/cosmosapjw-quantum/bass/pull/140
- 이전 단계 receipt: `publication/BACKUP_RECEIPTS.json`
- 복구 단계 receipt: `recovery/C07R*_BACKUP_RECEIPT.json` 및 최종 publication receipt

C07R0은 복구 시작, C07R1은 새 raw output 보존, C07R2는 보고서·판정·DAG까지 포함한 최종 단계다. 각 단계의 실제 업로드 완료 여부와 object ID는 해당 receipt를 따른다. C07R2는 research tree 전체, raw arrays, exact as-run source, provider tables, 검증된 native binary를 포함하는 **Git repository용 overlay**다. 나머지 runtime 의존성은 게시된 repo에서 가져오며, archive만으로 독립적인 전체 repo bundle이라고 주장하지 않는다. C06 Git 기준점은 위의 `304afc...` commit이다.

각 백업은 create-only이며 Git owner branch를 force-update하거나 merge하지 않는다. provider ACK·size·immutable identity 확인과 실제 restore 검증, 과학 검증을 분리한다. 캠페인 이름의 20261011은 한국 날짜 식별자이며 실제 복구 실행의 UTC 날짜는 2026-10-10이다.
