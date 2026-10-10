# He RCT coding-start: 최신 소스와 최소 접속점

이 문서는 외부 저장소 읽기만 수행한 intake 결과다. 새로운 원자 계산·소비기 실행·물리 승인을 주장하지 않는다. `INTAKE.json`은 관측한 commit/tree와 branch를, `SOURCE_IDENTITY.json`은 정확히 확보한 54개 파일의 Git blob 및 SHA-256을 기록한다. 모든 54개 파일은 최신 관측 tree의 blob identity와 일치한다. 기존 로컬 REI crate를 재사용한 27개 파일도 최신 원격 blob과 일치한 뒤에만 복사했다.

| 저장소 | 관측 branch | commit | tree |
|---|---|---|---|
| rei_bianchi | forward/rust-reion-kernels-20260922 | ccbc15019296b9128a90fa45b9c68c7daddc7b77 | 254d0221fe1c6aabbe37dfaf8e15eab74e67f623 |
| BASS_HE | research/shared-c64-crossrepo-20260928 | 21d5b8075429903d195d6e0e0c24a10c00b21063 | 4061b29b74c70936433efcf6ff57ad5921489204 |

REI는 직전 루프 종료 commit과 동일하다. HE는 직전 관측 97b38bbd1474aa7d8bd4244bae287ea026359de5 이후 DELIVERY_RECEIPT.json 한 파일만 추가했다. 새로운 RCT 물리·구현 변경은 없다. 이후 owner가 게시할 때에는 moving branch를 다시 읽되 과학 근거를 이 관측 commit에서 다른 commit으로 묵시적으로 바꾸지 않는다.

## 현재 선언과 적용 범위

REI `runtime_inputs/closure_process_decision.json`의 현재 모형은 `R1HomogeneousSuccessor_SYNTHETIC_HHE_3GROUP_V1`이며 `He2_H_CX_RCT=false`, `He2_H_CX_NRCT=false`다. 이 OFF는 선택한 baseline의 범위이며 물리적으로 RCT가 무시할 만하다는 결론이나 실제 원자율 0이라는 뜻이 아니다. 현재 사용자 요청은 별도 bounded RCT extension을 시작하는 새로운 의존성을 제공한다. 기존 baseline 계약을 소급해서 ON으로 고치는 것은 필요하지 않다.

HE `CURRENT_FASTEST_STATE.json`은 `WAIT_OWNER_OPT_IN_AND_PROVIDER_CONTRACT`, actual RCT binding 미수락이다. `HE-F2B/data/OWNER_SCOPE_BINDING.json`은 generic REI-F00/F01의 회수를 이미 인정한다. 따라서 과거 HE-F2의 "canonical contract missing"을 지금의 일반 blocker로 반복하면 안 된다. 현재 부족한 것은 **RCT를 선택한 구체적인 소비기 모형·source instance·closure·실제 adapter**다. HE-F2B는 과거 FT03의 30000–110000 K guard가 현재 synthetic F03 baseline에는 적용되지 않는다고 명시한다.

## 사용할 수 있는 공급기 자료

| source id | k [cm³ s⁻¹] | source numerical call domain [K] | 의미 |
|---|---:|---:|---|
| GM25_W82_RCX_CONSTANT_200_10000_K_V1 | 1.70e-13 | 200–10000 | literature constant fit, precision/physical uncertainty 미인증 |
| KF96_HEIII_HI_RCT_NOMINAL_V1 | 1.00e-14 | 1000–10000000 | nominal compilation prescription; 원문 lower endpoint는 근사 표기 |

두 source는 같은 반응의 대안이므로 더하지 않는다. 공통 지원 구간에서 별도 run의 sensitivity로만 비교한다. 17배 차이는 통계 오차막대나 엄밀한 물리 상계가 아니다. packet은 SI m³ s⁻¹ 값을 함께 제공하므로 CGS consumer에서는 정확한 단위 변환을 한 번만 한다. source의 null photon/heat/recoil moments는 그대로 보존한다.

`HE-F1/data/{GM25,KF96}_PACKET.json`은 event-count coefficient view다. `HE-F2/he_f2_binding.py::provider_candidate`는 실제 `thermal_rate` view가 있어야 common provider schema에 올리는 점을 명시한다. event-count packet 전체를 이름만 thermal_rate로 바꾸지 않는다. 새 RCT adapter는 동일 source scalar와 event stoichiometry를 별개 필드로 추적하거나 공급기의 정식 thermal-rate view를 반환해야 한다.

## 실제 코드와 최소 접속점

`rust/rei_microphysics/src/atomic_provider.rs`의 `AtomicProvider`는 concrete raw-reference 객체다. 범용 trait 또는 RCT variant가 없다. 모든 `RawRecord.consumer_admission=false`이며 현재 K1–K6 및 cooling channels는 electron-impact/recombination 계열이다. 여기에 RCT를 K4/K6처럼 끼워 넣으면 density pair와 electron stoichiometry가 달라진다.

`hhe_events.rs`의 `HHeModel`은 nH,nHe,3×3 photo cross sections,3 recombination coefficients,3 electron-impact coefficients를 가진다. `hhe_rhs`는 HII/HeII/HeIII fraction, proper thermal energy density, 3 proper photon number densities의 7차원 RHS를 돌려준다. recombination radiation은 별도 escaped energy reservoir로 빠진다. HHeEvents에는 9 photo,3 collision,3 recombination counters만 있고 RCT event counter나 escaped photon-number counter는 없다.

권장 최소 접속점은 별도 `he_rct` module이다. 독립 selector/provider contract, RCT event RHS, 명시된 closure ledger와 명시적 opt-in consumer wrapper를 구현하고 기존 `hhe_rhs` baseline은 유지한다. Default OFF는 source 미선택을 물리적 k=0으로 바꾸지 않는다. RCT의 분율 기여는 nH,nHe>0에서 `(R/nH, R/nHe, -R/nHe)`, `R=k nHI nHeIII`. 이 식은 `nH dxHII+nHe(dxHeII+2dxHeIII)=0`을 만족한다. zero-nucleus 한계에서 0/0은 별도 정책으로 거부하거나 밀도좌표를 사용해야 한다.

closure를 mono-Q escape로 선택할 경우 반드시 consumer approximation으로 기록한다. Q=chiHeII−chiHI=40.819325400298 eV이며 chiHeI는 상쇄된다. 별도 escaping photon-number ledger에 +R, escaped energy에 +Q R, chemical binding에 −Q R, direct thermal에 0을 둔다. 이것은 scalar k가 제공한 광자 에너지/열 moment라는 주장이 아니다. 현행 photon groups의 대표 에너지 13.7/24.7/54.5 eV는 Q와 다르므로 임의로 한 group에 주입하면 photon number와 energy가 동시에 맞지 않는다. Transport closure를 원한다면 별도 spectral projection이 필요한 후속 과제다.

`microstep.rs::implicit_hhe_step`는 photo/collision/recombination 구조에 맞춘 analytic positive block update이며 `hhe_rhs`를 직접 부른다. RHS wrapper만 추가해도 기존 stepper가 자동으로 RCT를 적분하지 않는다. `thermal::endpoint_thermal`과 `be_endpoint_residual`도 기존 세 반응 종류에 맞춘 코드다. 이번에 adapter/RHS 검증까지만 구현하면 반드시 time integrator admission 미수행을 기록한다. 실제 stepper extension은 RCT event ledger와 residual, accepted half-step event 합산 및 energy invariants를 함께 확장해야 한다.

## 재사용할 검증과 유지할 gate

기존 `tests/hhe_events.rs`에는 EOS/electron density, total RHS energy, photo event ownership, integrated event counts/BE residual, zero duration, rejected-state immutability, pure H/He limits가 있다. `tests/atomic_provider.rs`에는 original C point values, Verner thresholds, source authority/domain checks가 있다. 이번 변경 범위에는 RCT 선택·단위·정확한 density pair·분율 정규화·electron/nuclei conservation·escape number/energy·온도 경계 거절·OFF baseline parity를 별도로 추가하는 것이 의미 있다. 기존 source correctness test 결과를 RCT의 물리적 정확도로 이전하면 안 된다.

REI-F09의 paired campaign은 REI-F08/HH-F2/HE-F2를 입력으로 하는 기존 공동 sensitivity node다. 이번 coding-start adapter 자체는 F09 campaign 완료가 아니며 HE-F3/HH-F3에서 별도의 같은 cosmology history를 중복 실행하지 않는다. F04 map/derivative enclosure, 역사적 strict local gate 실패와 public-width gate, 원자 HE-L1/L2/L3 lane은 그대로 남긴다. 새 bounded extension은 그 gate를 승격시키지 않는다.

HE의 현재 AGENTS.md는 독립 재구현임을 명시하고 source/derivation/numerics/conjecture를 구분하며, 첨부 PDF 재배포를 금지하고 changed dependency 없는 heavy suite 반복을 금지한다. REI 관측 tree에는 AGENTS.md가 없었다. 이 intake는 공개/연결된 저장소의 텍스트 code/contract를 확보했으며 첨부 PDF를 재게시하지 않았다.
