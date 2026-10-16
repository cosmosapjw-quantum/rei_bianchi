# 원본 native Grackle 열화학 transaction

연구 base는 PR157 `710f08b2bebaefbd6a28690d450d759877053ebb`, 실행 native는 PR150 `a42fd7c9849306074a9f7a262628cd852ce34dea`이다. 기존 native science source를 수정하지 않고 원본 `Driver::chemical_stage`를 그대로 호출한다. 이 함수는 매 Newton trial의 EOS T에서 원본 RR/CI/DR/CE/freefree/CMB를 재평가하고 같은 trial opacity의 원본 `PreparedAbsorption` backward-Euler survivor와 결합한다. native Newton 잔차 1e-11, 최대 50회 및 기존 line-search를 그대로 유지했다. 새 Newton solver나 합성 계수는 없다.

`native_bind.rs`의 연구 wrapper는 accepted gas, 네 photon 배열, 누적 physical ledger, proper time, source cursor와 emission cohort를 clone한다. trial에서 source를 한 번 주입하고 원본 implicit stage 및 각 transaction/cumulative invariant를 검사한 후 성공한 bundle만 commit한다. 실패는 원 accepted bundle에서 dt를 반으로 줄여 최대 20회 재시도한다. invalid dt는 RHS 호출 없이 즉시 오류다. 양의 w/N, gas simplex, recovered T∈[1,1e6] K를 검사하며 clipping은 하지 않는다. physical ledger 허용값은 원 계약의 1e-10 × 실제 reservoir/exchange 절댓값 합이다. `transaction_checks` 각 행은 [raw residual, physical scale, normalized residual]이며 순서는 energy(eV/H), photon number(H^-1), charge(H^-1), HII/HeII/HeIII stocks(H^-1)이다. cumulative 값은 `invariants`에 단위 이름으로 기록한다.

고정 geometry 실험은 a=.1(z=9), native cosmological nH0/nHe0, native Tcmb=27.255 K와 reaction h=0이다. native background q_ref=0/±.1에서 실제 b를 읽는다. delta는 current physical 20/40/80 eV로 정하며 reference q=E/native ray.scale로 변환하여 다른 ray에 놓는다. 저장 count는 photons/H, reference energy moment는 q*N eV/H이다. 원본 geometry와 rates는 유지한다. main manifest는 실행 전에 `frozen_manifest.json`에 쓴다. RR-dominated 8000 K, CI-dominated 1e5 K, mixed-photo 1e4 K의 32/64/128 시간 격자와 T=100/10 K, no-He, tiny-ions, 강한 흡수, early/delayed pulse, native MD14, signed geometry controls를 실제 적분했다. 모든 integrated trajectory에는 원본 모든 과정이 활성화된다.

사용법(표준 Rust/Cargo, Python 3; native 원본과 9개 외부 include_str 입력 필요):

```bash
export NATIVE_ROOT=/path/to/pinned_native_export
export PYTHON=python3
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh campaign
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh refinement
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh cohort_refinement
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh temporal_refine
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh temporal_refine1024
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh tests
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh retry_test
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh stiff
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh stiff_rr
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh stiff_ci
bash research/rei_c16b_grackle_thermal_bind_20261016/run_native.sh dynamic
python3 research/rei_c16b_grackle_thermal_bind_20261016/tests_native.py
```

각 모드는 `evidence/native/<mode>/`에 frozen manifest, history JSONL, endpoint summary, rejected attempts, cohort, 실행 명령, exits와 `/usr/bin/time -v`를 기록한다. Cargo jobs=2, 기본 transport worker=1, 한 번의 serial/8-worker 대조, 8 GiB virtual-memory bound, campaign timeout=300 s, accepted≤20000, RHS≤4000000이다. source identity는 tracked native crate 전체를 exact PR150 Git blob과 비교한다. 실행 example/module는 연구 사본을 scratch example에 복사한다. 실행 crate의 소스/의존성을 교체하지 않는다.

Persistent RHS server:

```bash
NATIVE_ROOT/rust/rei_microphysics/target/release/examples/native_campaign rhs 0.1 0.0 1
```

stdin 한 줄은 `x y z w_erg_per_H N20 N40 N80` 7개 float다. stdout은 한 요청마다 flush한 JSON 한 줄로, `d=[dx,dy,dz,dw,Ndot20,Ndot40,Ndot80]`, 실제 E/σ, photo Gamma/Heat, 전체 원본 `IgmPointRhs`와 `IgmRates`를 반환한다. 이 서버는 native physics parity에 사용할 수 있으나 독립 계수 oracle은 아니다. 별도 reference worker가 literal-C Grackle + 독립 Python EOS/stoichiometry/cooling/CMB/Verner와 SciPy Radau를 작성했다.

Pulse source는 source edge를 정확히 나누고 총 0.02 photons/H를 early [0,1.5e12] 또는 delayed [1.5e12,3e12] s에 배출한다. 각 cohort의 t0/t1, midpoint emission time, emitted N/E와 observation-time emission age를 기록한다. source-off와 재시도가 birth를 중복 계산하지 않는지 검사한다. 이는 emission-age metadata이며 surviving photon age 분포/SSP lifetime을 추론하지 않는다. native MD14는 native emissivity 자체를 한 번 주입한다.

`refinement`는 같은 현재 geometry에서 국소 isotropic MD14 방출을 검사하므로 coordinate/grid/reflection 점검이다. 실제 방향별 redshift가 있는 `cohort_refinement`는 native a_ref=1/21,z=20에서 Δt_emit=1e14 s의 native MD14 cohort를 만들고 원본 `geometry_map`으로 a=.1,q_ref=+.1까지 옮긴다. 이후 custom gas와 local ledger origin을 새로 정하고 source-off local reaction을 적분한다. construction photon/thermal work는 별도 `construction` 배열에 보존하며 local energy ledger에 중복 적용하지 않는다. 이 배열의 순서는 birth a, current a, birth z, native emissivity interval, emitted N, emitted E, construction photon work, constructor-gas thermal work, current N, current E이다. z20→9 gas history를 계산했다는 의미가 아니다. source subdivisions 16/32/64, angles 8/16/32, transport cells 32/64/128은 서로 별도 축이다.

`tests`는 원본 native event를 이용한 photo-only/RR-only/CI-only의 **test-only event decomposition** 12개를 검증한다. 각 stoichiometry, H/He, charge, binding/thermal/escape identity를 확인하며 integrated provider를 교체하지 않는다. empty-photon full-native trajectory를 RR-only라고 부르지 않는다. `stiff`, `stiff_rr`, `stiff_ci`는 큰 초기 무차원 노출에서 finite/admissible backward-Euler transaction과 ledger를 확인한다. 이 coarse trial에 정확도 admission을 부여하지 않는다. `dynamic`은 원본 `Driver::adaptive_step`로 각 q_ref=0/±.1에서 3 accepted steps만 수행하고 실제 s/H, b, MD14 source 및 thermal/photon work를 기록한다. full cosmological history는 아니다.

본 결과의 한계는 고정한 native model/fixture의 transaction, 시간·격자 측정치, source interface이다. 경험적 fit의 보편 타당성, 일반 stiff 정확도, production cosmological ionization/T history, continuum certificate, escape spectrum, surviving SSP age physics, baryon recoil/Einstein backreaction은 입증하지 않는다. 최종 scoped 과학 판정은 독립 Astra 검토에 따른다.

실행 결과: `evidence/native/mechanical_summary.json`의 203 checks와 이번에 실제 실행한 원본 native focused tests 51개/7 targets가 PASS했다. 역사적 재사용 테스트와 구분한다. 46개 native trajectory summary의 transaction/cumulative ledger가 고정 기준을 만족했다. 최대 cumulative energy raw residual은 1.5311023560116155e-9 eV/H, physical scale은 16.811055522696243 eV/H, normalized 값은 0.9107711017577137이다. 이 값은 기존 bound보다 작으며 허용오차를 넓히지 않았다. mixed1024의 maximum normalized ledger는 0.8162137765143188, actual accepted/attempts는 모두 1024이다. 명령, 자원, steps, RHS counts, raw residual/scale은 `execution_summary.json`에 있다.

Pulse recovery 테스트에서 표현 문제를 발견했다. 원본 `add_delta`가 같은 q의 N과 q*N을 각각 더하지만 delta validator는 정확한 U=q*N을 요구하여 반복 주입 때 한 ulp 불일치가 발생할 수 있다. 첫 오류는 `retry_test_first_failure/`에 보존했다. 승인된 수정은 알려진 fixed-q pulse adapter에만 적용했다. 각 기존 occupied ray가 확실한 q 하나만 가지며 passive/unrelated stock이 없는지 확인하고, fresh complete PhotonState에 Nold+birthN을 넣어 native add_delta를 ray마다 한 번 호출한다. 원본 validator/science를 수정하거나 broad spectrum을 압축하지 않는다. source/cohort ledger는 실제 native inventory 차이를 쓰고 intended-minus-represented count/energy와 gross scale을 `emission_roundoff`에 기록한다. 이 표현 오차는 128*eps*scale 이하여야 한다.

기존 early/delayed의 32개 출력 구간은 표현 오류 때문에 147/87회 거부와 재시도를 거쳐 실제 76/68 accepted substeps를 썼다. 수정 후 두 사례는 각 32 accepted steps이다. 따라서 궤적 차이를 최종값의 roundoff 차이만으로 설명하면 안 된다. 표현 문제 때문에 생겼던 시간 세분화가 사라진 효과다. 기존 자료를 모두 보존하고 수정 자료는 `pulse_repair/`를 사용한다. 성공한 native trial을 테스트에서 한 번 거부하고 두 half step으로 재시도한 recovery bundle은 clean 두 half step과 모든 값이 같았다. source count는 한 번만 commit하고 cursor=2이며, 버린 trial의 RHS 호출은 별도로 계수했다. 독립 reference worker는 기존 cached Radau를 그대로 두고 수정 자료와 다시 비교했다.

혼합 광자 사례는 초기 coarse endpoint만으로 정확도 판정을 내리지 않았다. 전체 common-time photon transient 오차가 n128/n512에서 기준을 초과하여 같은 horizon/source/physics로 승인된 256/512/1024 refinement를 수행했다. coarse 원본과 실패 판정은 보존한다. 최종 accuracy/order/grid 결과의 authoritative 파일은 별도 `evidence/reference/`와 부모의 검토 판정이다. Strong absorption 및 stiff RR/CI의 초기 노출은 각각 86.8201194365, 10.0, 9.999999999999966(≈10)이며 각 단일 BE trial의 admissibility/ledger만 확인했다.

오프라인 archive를 새 디렉터리에서 검증할 때는 Git이 필요 없는 다음 스크립트를 사용한다. `NATIVE_ROOT`는 새/빈 디렉터리여야 하며 이전 실행파일을 재사용하지 않는다. intake source archive와 manifest의 원본 파일/9개 include_str 입력을 검증하고 fresh Cargo target에서 build한 뒤 native event/rollback/recovery controls 및 32-step full-native mixed trajectory를 실행한다. cloud별 실제 실행은 controller가 수행하며 `RESTORE_RESULT.json`, source identity, time-v와 exit를 반환한다.

```bash
NATIVE_ROOT=/new/empty/native_root PYTHON=python3 EVIDENCE_OUT=/new/evidence \
  bash research/rei_c16b_grackle_thermal_bind_20261016/restore_verify.sh
```
