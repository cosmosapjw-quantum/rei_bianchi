# IGM 두 단계 연구의 외부 결과 intake

2026-10-07. 이 intake는 읽기·source 회수·identity 확인이다. 기존 과학 suite를 재실행하거나 외부 저장소를 변경하지 않았다.

## 현재 원격 상태

| 공급원 | freshly observed branch HEAD | 최신 과학 결과 |
|---|---|---|
| BASS_HE | `02ca307e4e93e6a09ab5a1be91d229f5531988e8` | `9b46aab79eeafd452a5fb35b1c0fd00eef6f5683`, RCT02 기준 이력; `390ea183...` 전달 receipt |
| bass_cr | `6429f8df1356de2aa4f0a39c3545d0712594878b` | `d9522add1996e5f4fe482dfea6b18a9b79d87346`, CR-F0-R2 source-fed BE stage |
| bass | `e57064934bb176b08d2072aa537e5f71a430ae5e` | 기존 `1e45e0f48cd83dcb21c23d4087fa5526195331d7` 이후 SYNC03 문서만 추가 |

위 source/ref/최근 commit와 tree는 raw/에, 읽은 원문은 sources/에 있다. root intake의 IGM HEAD는 `39c39eab1cc2f1a215723680accc123e67ef13b6`다.

## 직접 재사용 가능한 것과 경계

**CR-F0-R2**는 실제 광자 source-fed implicit 단계다. `SourceState { gas: IgmGasState, photons: Vec<CountPerH> }`; `implicit_source_step(mode, old, ctx, injection, dt, provider, control, cr)`가 source와 흡수를 BE로 소거하고 가스 네 변수 Newton을 푼다. `trial_source_step(..., accuracy, ...)`는 full/two-half를 만들고 `SourceTrial::accept()`가 half1+half2의 사건만 누적한다. `ledger_residuals`는 source-only 단계 양끝의 photon energy 변화가 있으면 거절한다. 모든 source는 photons/H/s, proper nH/nHe는 cm^-3, w는 erg/H다.

따라서 단계내 고정 nH,nHe,H,Tcmb,E,S라는 계약을 보존하면 source-stage 비교용으로 쓸 수 있다. cosmological clock, source birth, redshift와 lower-boundary crossing은 구현 밖이다. 현재 장기 FLRW의 경계 횡단 오차를 해결했다고 간주할 수 없다. CR-on은 MissingAuthority이고 OFF에서 deferred witness 호출 0이라는 범위만 검증되었다.

실제 ZIP `BASS_CR_FASTEST_STEP_20261007_v1.zip` 196491 bytes, SHA256 `f3156ba8e07d4cfe263cb793c424a66958fa9730cbe9c1779c96007e10a11434`를 Drive `1gHvXdZGWL9LO3QCBHcg0cHZRpyHhRpvt`에서 내려받아 SHA/CRC/80 payload manifest를 확인했다. `archives/`와 `restored/BASS_CR_FASTEST_STEP_20261007/`에 존재하며 `ARCHIVE_INTAKE.json`이 기록이다. 새 과학 실행은 없다. source-step의 전체 Rust source는 이 archive에 있으며 Git의 launcher만으로 source 자체가 게시된 것은 아니다.

현재 IGM tree와 CR의 원 library 27개 비교에서 25개 blob가 같다. `atomic_provider.rs`, `lib.rs`가 다르므로 공급자의 전체-source exact guard를 자동 통과시킬 수 없다. atomic_provider diff를 읽으면 Verner cutoff 상수를 별도 공개 함수로 옮긴 변경과 cfg(test) 호출수 instrumentation이며 기존 수치 계수·분기값은 유지한다. 이는 source review이며 새 컴파일/수치 parity 실행 결과가 아니다. lib.rs는 현재 IGM module export를 보존하면서 add-only import해야 한다. 기존 26-source equality guard를 무조건 끄면 안 된다.

**HE RCT02**는 `point(state, nh, nhe, h, tcmb, photo, RctSelection)`의 native RHS를 DOP853/Radau로 시간적분한 독립 시간적분기 비교다. Optional RCT point source 및 thermal/escape ledger는 이미 존재한다. KF96/GM25 공동 actual EOS-T guard는 [1000,10000] K다. 기본 OFF 및 물리적 원자 photon moment 미결정 상태는 유지한다. 7개 source-free 제조모형 × 3설정과 1개 후속 × 2설정, 총 23 ODE solve/960 accepted steps/14758 native evaluations를 supplier가 보고했다. 두 integrator는 같은 native RHS를 공유하며 independent atomic validation이나 rigorous flow certificate가 아니다. 실행 chemistry4blob는 current IGM과 같다. photon/source-coupled receiver adoption은 아직 열려 있다.

RCT02 archive SHA256 `8fe8cea867250e77077acfc542c5d2326844d7fea1f2162183ac4c67555c9f01`, 1975826 bytes; Drive `1lNG5-ie677XV_Fqz3JZ_z-ZLYlaiOkHK`, Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_FAST_IGM_RCT02_HISTORY_20261007_sha_8fe8cea86725.zip`. 이 intake에서 archive 자체는 내려받지 않았고 source 문서·receipt·point.rs만 읽었다. 따라서 RCT02 reference 숫자는 supplier-reported이며 재실행/독립검증하지 않았다.

RCT는 H I + He III -> H II + He II + photon이다. event/H/s를 J라 두면 direct dx_HII=J, dx_HeII=J/fHe, dx_HeIII=-J/fHe이므로 direct electron/H 변화는 0이다. binding 변화=-Q J, thermal=(Q-Ebar)J, escape=Ebar J로 상쇄한다. electron/opacity 영향은 온도 및 다른 반응의 되먹임으로 나타난다. Ebar=Q라도 전체 온도 이력이 OFF와 같아야 한다는 테스트는 잘못이다. 이 관계는 회수된 point 구현의 물리적 조합을 읽어 정리한 것이고 새 cosmological RCT 실행은 아니다.

**BASS**의 `integrate_clock_visibility(RayClockGrid, normal_rates_s_inverse, observer_optical_depth)`는 완성된 실제 IGM 이력을 소비할 수 있다. proper ne -> cm^-3에서 m^-3로 10^6, q_t=c sigma_T ne D이며 D는 한 번만 적용한다. conformal seconds에서 q_eta=a q_t; conformal length에서 q_chi=a q_t/c다. `RayClockGrid`의 frozen-cell exact a_eff는 Delta t/Delta eta이고 시간가변한 실제 rate에 대한 정확도를 뜻하지 않는다. 일반 ne/matter frame은 직접 `ElectronState`로 넣고 FT03 형식을 IGM으로 재명명하지 않는다. BASS는 lower-boundary 또는 coupled time-step blocker를 고치지 못한다.

## 이번 작업에 대한 선택

1. 우선순위는 IGM 자체의 장기 radiation boundary/coupled error를 해소하는 것이다. 외부 원자 정확도 연구나 CR-on을 이 critical path에 두지 않는다.
2. CR source-step은 actual-source 비교기나 별도 opt-in 공급원으로 재사용 가능하다. 현재 production IGM stepper를 이 고정-context 연구 stepper로 대체하지 않는다.
3. 수학/물리 확장은 합격한 경계 표현 위에서 source, absorption, redshift work와 number/energy의 정확한 분해 또는 IGM 실제 이력의 관측량 전파가 적합하다. 기존 F08 그림 재사용은 이 IGM 범위의 새 결과가 아니다.
4. Optional RCT03 receiver 채택은 source-free RCT02 finite reference부터 시작할 독립 lane이다. 현재 lower-boundary 해소 작업과 무관하며 source-driven RCT/physical spectral closure를 완료했다고 간주하지 않는다.

새 solver/리뷰 결과는 이 intake와 구별하여 root loop evidence에 기록한다.
