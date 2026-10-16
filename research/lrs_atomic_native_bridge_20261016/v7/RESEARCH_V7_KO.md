# REI-LRS V7: 실제 native source-on 유한 구간 시간 수렴

2026-10-16 KST. V6 PR #161 `4e292a44e71dfca35d551c754fc1a64151c368c7`의 source-free midpoint 결과를 실제 PR #150 native FLRW source-on 경로와 비교했다. Native owner는 `6ea2b1b4b3875c9163cafc45efe720afded43fc4`로 고정했다. 원본 production 코드와 checkpoint는 수정하지 않았다.

## 물리와 변경

원본 `Driver::fixed_step`은 geometry 반 단계, 전체 MD14 photon source 주입, backward-Euler photon 흡수와 coupled H/He chemistry, geometry 반 단계 순서다. 별도 NCP 소스 복사본에서 V7 실험 함수는 재결합 RR/DR half step, RR/DR을 제외한 원래 native BE chemistry, 재결합 half step을 적용한다. RR/DR subflow는 V6의 양수성 보존 exact-pair map과 자기일관 온도 midpoint를 Rust로 옮겼다. `igm_rates.rs`의 Grackle 3.4.1 Case-A RR/DR·cooling 수치는 변경하지 않았고 10,000–24,000 K 안에서만 V7 결과를 인정한다. 실험 코드와 재현 생성기는 `build_experimental.py`, 실행기는 `native_refinement_v7.rs`이다.

이 변경은 source/opacity의 BE 시간 배치, CI/CE/freefree/CMB의 BE 갱신을 유지한다. 따라서 RR 온도 midpoint의 국소 개선만으로 전체 source-on 2차 수렴이 따라오지 않는다. 일정 source와 opacity에서도 한 단계 source를 먼저 모두 넣고 BE 흡수하면 정확한 동시 주입·흡수 적분과 O(Δt²)의 국소 차이가 남는다.

## 실제 NCP 조건과 검증

호스트 `s1a0e5abed09`, Python 3.12.3, Rust 1.99.0, 64 logical CPU/125 GiB RAM. 시작 시 별도 R9 T4 worker가 약 12 CPU를 사용 중이어서 V7 native transport thread는 사례당 2, Cargo build job은 2로 제한했다. FLRW `q_ref=0`, `a0=1/21`, 공통 `X=ln(a/a0)` 구간 `[0,1e-5]`, 초기 `(xHII,xHeII,xHeIII)=(.075,.12,.03)`, `Tgas=15000 K`, 빈 photon field, MD14 escape fraction .2, 64 transport cells, 8 angular nodes, 16 source energy subdivisions, native total-H/He nuclei density를 사용했다. 각 방법을 `N=16,32,64,128` 고정 단계로 실행했다. Proper-time 전체 길이는 약 `8.4495e10 s`이다.

초기 기체를 바꾼 뒤 driver의 초기 총에너지 기준도 해당 상태에서 다시 계산했다. 원본과 실험 빌드의 동일한 생성 가능 초기 상태(He 핵은 있으나 초기 HeII=HeIII=0)에서 16단계 전체 `DriverState` 출력은 바이트가 같았다. 최종 실험 소스에는 원본과 동일한 매 스텝 number/energy `1e-10` gate와 cumulative `1e-8` gate가 들어 있다.

| 방법 | N=128 Tgas (K) | T 수렴차수 (16→32→64, 32→64→128) | photon N 차수 | photon U 차수 | N=128 wall |
|---|---:|---|---|---|---:|
| 원본 native BE | 14988.768644287 | 1.00007, 0.99999 | 1.1073, 1.0588 | 1.0737, 1.0403 | 0.340 s |
| V7 RR midpoint + native BE remainder | 14988.768644120 | 1.00006, 0.99999 | 1.1073, 1.0588 | 1.0737, 1.0403 | 0.415 s |

원본 및 수정본 각 4/4 계산이 exit 0이다. `cargo test --test axbi_driver`는 13/13 PASS, 새 source-free Radau reference 표적 pytest는 2/2 PASS. 실행 480개 accepted step 전체에서 온도는 14988.768–14999.912 K, 분율은 양수다. 최대 누적 photon-number 잔차는 `2.65e-22/H`, 전체 에너지 잔차는 `7.12e-11 eV/H`, Newton 결합 잔차는 `2.08e-12`였다. 최대 매 스텝 에너지 잔차 증분은 `4.57e-12 eV/H`, 전자 사건 잔차는 `1.76e-13/H` 수준이다. H와 He 핵수는 neutral complement를 포함한 native 상태식으로 각각 보존된다. 최종 T에서 source/opacity/thermal/binding/escape/expansion work를 포함한 전체 native ledger가 닫힌다. RR/DR cooling만의 독립 누적 열량과 최대 photon opacity exposure는 이번 CSV에서 별도 계측하지 않았다.

독립 `reference/radau_casea_reference.py`는 PR #150의 literal Case-A RR/DR와 냉각을 129개 원본 table 온도에서 정확히 재현하고, 같은 FLRW 밀도·H(a)에서 **source-free RR/DR+adiabatic subset**의 연속 ODE를 푼다. 최종 T는 14999.701216 K, 에너지 상대잔차 `1.35e-16`, 핵수 잔차 0이다. Native source-on에는 photoionization, CI/CE/freefree/CMB가 추가되므로 이 Radau 끝값을 native 전체계 정확도 오차로 사용하지 않는다. Rust midpoint RR-only 연산자와 Radau를 직접 대조한 계산도 이번 단위에는 없다.

## 과학 판정

- **PASS, 제한 범위:** 원본 PR #150 source-on FLRW 유한 구간의 실제 4해상도 실행, 원본 고정 간격 단계의 대조 상태 parity, V7 RR/DR midpoint 실험본의 양수성·number/electron/전체 energy ledger 및 표적 테스트.
- **HOLD:** 전체 source-on 2차 수렴. 양 방법의 T와 photon observables는 실제로 약 1차다. RR/DR 단독 native–Radau 정확도, RR 냉각 분리 ledger, photon opacity exposure도 별도 증거가 없다.
- **HOLD:** Case-B 재결합 photon 재수송, full EoR history, signed Bianchi I 확장 및 production activation.

실제 실행 명령, 소스·입력 SHA, 최초 시도와 target repair, exit code, 모든 해상도의 per-step CSV·stderr·CPU/wall/RSS는 `evidence/ncp_20261016T0118Z/V7_EXECUTION_RECEIPT.json`과 `raw_evidence_v2.tar.gz`에 있다. 실행 실패는 관측되지 않았다. 독립 검토가 발견한 첫 결함은 experimental 단계의 per-step gate 누락이었고, 한 번의 표적 수정 뒤 재실행했다. 관측된 1차 수렴은 남겨 둔 photon/source/BE 시간 배치의 코드상 오차 기작과 일치하며, Grackle rate 데이터 실패의 증거는 아니다. 최대 관측 `Δt × n_e × α`는 `1.26218e-6`으로 강성 영역은 시험하지 않았다. 다음 최소 단위는 **native RR/DR 전용 단계와 Radau 직접 비교 및 냉각 분리 회계**이고, 그다음 source-age 주입과 photon attenuation의 시간 중심화를 같은 구간에서 비교한다. 해당 단위 전까지 native whole-history 정확도는 승격하지 않는다.
