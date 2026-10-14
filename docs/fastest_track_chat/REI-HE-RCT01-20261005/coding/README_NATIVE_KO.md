# He RCT native consumer 준비

새 파일 `src/he_rct.rs`, `tests/he_rct.rs`, `examples/he_rct_probe.rs`와 `src/lib.rs`의 additive export만 변경했다. 기존 `hhe_rhs`, `atomic_provider.rs`, `microstep.rs`, thermal/F04 및 FLRW 모듈의 수식과 동작은 변경하지 않았다.

이 구현의 반응은 HI + HeIII → HII + HeII(1s) + γ다. Gas-rest common-temperature Maxwell 분포, zero drift, H(1s), W82에 대응하는 4He 시나리오를 명시적으로 선택한다. KF96 자체의 isotope 미해결 상태는 metadata에 남아 있다. 새 원자 산란 계산 또는 source의 physical admission이 아니다.

`RctProvider::new`는 KF96 nominal 또는 GM25 constant 중 하나와 17배 source conflict의 명시적 인지를 요구한다. 기본 source가 없고 source 자동 전환·합산·clamp·외삽을 허용하지 않는다. 온도는 기존 HHeModel의 EOS로 state에서 복원하여 해당 provider의 strict numerical window를 검사한다. 정확한 공급자 endpoint는 `coefficient_cm3_s(T)` 또는 probe의 `rate` 명령으로 검사한다. Probe의 요청 온도로부터 state를 만드는 과정은 보통 binary64 산술이며 endpoint 보정은 하지 않는다.

`events()`는 R = k nHI nHeIII, species 변화, fraction 변화, emitted photon number, chemical energy 변화를 계산한다. 상태 차원은 proper cm^-3이고 time은 proper s다. Species 순서는 HI,HII,HeI,HeII,HeIII,e이며 변화량은 (-1,+1,0,+1,-1,0)R다. Fraction 순서는 xHII,yHeII,yHeIII다. 분모에 해당하는 nuclear density가 0이면 해당 RCT fraction derivative를 0으로 둔다. 양 핵밀도가 모두 0인 모델은 기존 모델이 거절한다. 이 convention은 기존 HHe RHS의 absent species용 virtual per-capita convention과 분리된다.

Count-only 결과의 `thermal_photon_closure`는 `IncompleteScalarOnly`다. 열 moment·광자 에너지 moment·spectrum의 부재를 0으로 채우지 않는다. 따라서 count-only 결과를 enabled wrapper로 전달하는 API는 없다.

`EscapingMeanPhotonEnergy::research_input_ev`는 유한하고 **엄밀히 양수**인 caller-supplied event-weighted mean photon energy를 받는다. 해당 반응에서 실재 photon 한 개를 방출한다는 선언 때문에 0은 거절한다. 이 domain guard가 물리적으로 가능한 mean-energy 범위나 실제 spectrum을 확정하지는 않는다. `closure_input_origin=CALLER_SUPPLIED_NO_ATOMIC_MOMENT`이며 실제 입력값, 시나리오 출처와 채택 근거는 외부 run manifest가 소유한다.

Q = model.threshold_HeII - model.threshold_HI > 0를 검사한다. Closure는 dUchem/dt = -QR, du/dt = (Q-Ebar)R, dEescape/dt = Ebar R를 eV→erg 변환하여 계산한다. Ebar > Q일 때 열 항은 음수다. 이 signed heat는 에너지 보존에서 도출한 조건부 총 translational balance이고, 독립적인 recoil 또는 열 전달 moment 계산이 아니다. Photon 한 개는 명시적 escape ledger로 나가며 기존 3개 photon group에는 추가하지 않는다. 해당 optically escaping mean-moment closure의 physical admission은 false다.

`combined_hhe_rhs()`는 기존 `hhe_rhs()`를 실제 호출한다. 기본 `RctSelection::Disabled`에서 모든 baseline 값은 bit identity를 보존한다. `Escaping {provider,closure}`는 RCT의 세 fraction derivative와 thermal/escaped energy만 더한다. 기존 photo/collision/electron-recombination 배열은 그대로 남기며 RCT ledger를 별도 반환하므로 RCT를 전자 재결합으로 오인하지 않는다. **Production microstep/implicit residual/time stepper에는 아직 연결하지 않았다.**

검증 증거:

- `BASELINE_GAP_LOG.txt`: 구현 전 import 실패 E0432. 최초 shell은 cargo exit code를 별도로 보존하지 않았으므로 status에 그 제한을 기재했다.
- `TARGETED_TEST_LOG.txt`: source/domain, count-only, conservation, zero-density, signed heat, finite overflow, actual baseline composition 등 20개 targeted test 통과.
- `PROBE_BUILD_ATTEMPT_1_FAIL.txt`: 최초 probe JSON format 문자열의 closing brace compile 오류를 보존했다. 출력 포맷만 수정했고 `PROBE_BUILD_LOG.txt`에서 빌드 성공했다.
- `PROBE_SMOKE_INPUT.txt`, `PROBE_SMOKE_OUTPUT.jsonl`: exact rate endpoint, count-only, explicit closure, OFF의 5행 JSON 실행 결과.
- `NATIVE_IMPLEMENTATION_STATUS.json`: 실제 exit status와 파일 SHA-256. 이 native 작업자는 전체 crate suite를 실행하지 않았으며 root의 최종 통합 검증 기록을 별도로 따른다.
- `BASELINE_PRESERVATION.json`: 동시 유입된 FT03를 포함한 최신 baseline의 변경 범위. 초기 27-file 검사는 PRE_FT03 기록에 보존한다.

실행 계약과 CLI field 이름은 `INTERFACE.json`에 있다. 외부 framework dependency는 추가하지 않았다.

## 동시 유입된 FT03에 대한 최소 통합

이 루프 중 기존 branch에 FT03가 들어왔다. `Ft03Model.gas`의 legacy alpha/beta는 0이고 실제 RR, CI, 두 DR channel은 `ft03_rhs`에서 온도 의존 공급기를 통해 계산한다. 그러므로 `combined_hhe_rhs(&ft03.gas,...)`를 소비 adapter로 사용하는 것은 이들 반응을 잃는 실제 오류다.

별도 typed `combined_ft03_rhs(&Ft03Model,&HHeState,RctSelection)`를 추가했다. 반환형 `CombinedFt03RctRhs`는 실제 Ft03Rhs baseline/combined와 별도 RCT ledger를 보유한다. FT03의 모든 photo/RR/CI/DR 배열을 그대로 보존하고 RCT fraction/heat/escaped-energy 항만 더한다. OFF는 실제 FT03 baseline의 bit identity를 보존한다. 이 함수도 RHS 단계이며 FT03 implicit stepper 또는 residual에는 연결하지 않는다.

현재 FT03 온도 domain 30,000–110,000 K는 KF96의 numerical window 안에 있다. GM25의 200–10,000 K와 교집합이 없으므로 FT03에 GM25를 강제하면 거절한다. GM25 비교에는 별도로 일치하는 low-temperature consumer 모델이 필요하며 자동 extrapolation/switch를 하지 않는다.

새 네 시험은 FT03 OFF identity, nonzero RR/CI/DR 보존, legacy gas adapter를 쓰면 실제 항이 빠지는 negative control, source domain 교집합을 다룬다. 총 targeted 24개 통과, probe 재빌드 성공. `FT03_PROBE_SMOKE_OUTPUT.jsonl`은 count-only·closed KF96 및 GM25 hot-domain 거절을 실행했다. 앞선 `TARGETED_TEST_LOG.txt`의 20개는 FT03 추가 전 기록이며 최종 전체 통합 로그는 root가 소유한다.
