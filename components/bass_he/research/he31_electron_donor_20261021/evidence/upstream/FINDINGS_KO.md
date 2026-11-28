# HE31 upstream delta와 H/He → Thomson 재사용 조사

검사 시각: 2026-10-21 13:08 UTC 전후. 담당 범위는 읽기 전용 R2/C2 소스 조사이다. GitHub 두 저장소의 최근 갱신 PR 각각 15개, 해당 PR branch/head, 단일 고정 canonical source tree와 관련 donor/생성기 계약만 확인했다. 과거 전체 branch audit를 반복하지 않았다. **새 과학 실행 0, 벤치마크 0, 저장소 수정·게시 0**이다. 이 디렉터리의 조사 산출물만 작성했다.

## 1. 지금 구현 방향을 정하는 결과

**기존 canonical D3 full40 모델은 이미 proper electron density를 받아 photon Thomson 항에 연결할 수 있다. 새 물리 효과를 구현하는 데 photon/neutrino hierarchy 자체를 다시 만들 필요가 없다.** 실제 필요한 것은 출처, 단위, epoch 범위가 결속된 donor 입력과 새 과학 identity다.

검사한 실제 cosmological donor는 모두 z=20→4까지다. 기존 original q=0 full H/He 결과는 312,238행이며, 별도 B1 R15 결과는 Q filling-factor 모델이다. 둘은 물리 입력이 다르다. z=20→2 실제 donor는 이번에 읽은 범위에서 발견하지 못했다.

Rust 생성기는 존재하지만 단순히 end_zbar=2를 넣어 실행할 수 없다. DriverConfig와 photon source가 각각 z≥4를 강제한다. 최신 PR199의 실제 driver/source 원문도 PR147과 동일했다. 따라서 우선 **엄격한 z20→2 consumer 준비 + 실제 z20→4 입력의 명시적인 부분구간 실행**을 완성할 수 있다. 완전한 z2 donor를 새로 만들려면, 원본을 보존한 별도 HE31 조건부 source/scenario를 정의한 후 계산해야 한다. 파일의 기존 범위 제한을 지우고 과거 모델과 동일하다고 주장하는 것은 근거에 맞지 않는다.

## 2. 12:39 이후 실질 변화

| 항목 | 현재 고정 head | 관찰 |
|---|---|---|
| [BASS_HE PR83](https://github.com/cosmosapjw-quantum/BASS_HE/pull/83) | e173f373cd481864d0395e3a7a76520615a80e1a | open/draft, 12:39:15 갱신. 기준 HE30에서 추가 변화 없음 |
| [REI PR216](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/216) | 1f32cc442ebde284bbb944455ba96066c9e0e055 | open/draft, D8 bracket 게시본 동일 |
| [REI PR215](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/215) | d669298f05286728453840da46cae958a3709456 | open/draft, ACCEL02 동일 |
| [REI PR199](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/199) | eb8042b729051f4700bd5d88d6781c4620009bcb | baseline744438f 이후 2커밋. D8 저장 표본 bracket와 게시/readback 추가 |

PR199 새 커밋은 a3cb0606341688affb6aea29990e960e53188d32와 eb8042b729051f4700bd5d88d6781c4620009bcb다. 바뀐 파일은 D8_LATE_SIGN_CROSSING_SAMPLE_BRACKETS와 UNIFIED_DAG의 관련 자료다. **새 donor, 새 Thomson kernel, 새 H/He 생성기 결과는 아니다.** 정확한 PR 목록과 diff 파일명은 UPSTREAM_DELTA.json에 있다. PR 제목에 나타나는 인접 AGE/원자물리 작업의 내용으로 조사 범위를 확장하지 않았다.

이는 검사 시점의 bounded 관찰이다. 모든 브랜치나 백업에서 full z2 donor가 존재하지 않는다는 전역 부재 증명은 아니다.

## 3. 즉시 재사용할 D3 full40 인터페이스

원본 고정 commit:

- REI PR147: 3b85dedce84d37b3e165da00685a8a984950aafe.
- research/rei_bass_hierarchy_backreaction_20261015/canonical_fv_20261015/canonical_fv.py.
- 같은 상위 경로의 species_hierarchy.py, lrs_boltzmann.py.
- 로컬 동일 source는 BASS_HE/research/he29_rei_pilot_20261021/vendor/에 있다.

CanonicalFVSpecies 생성자의 ne_source가 SpeciesHierarchy로 전달된다. fields(x,y)는 a=a_ref exp(x)를 구하고 ne_source.density(a)를 호출한다. 인터페이스는 **proper electron density [cm^-3]**다. 이미 proper density이므로 a^-3을 다시 곱하지 않는다.

충돌률은 Gamma_T=c sigma_T n_e [s^-1]이고, 독립변수가 x=ln(a/a_ref)이므로 RHS의 감쇠는 Gamma_T/H다. canonical_fv.py는 mass stress를 반영한 실제 H로 이 비를 계산한다. photon energy multipole와 number multipole에 둘 다 적용되며, neutrino energy/number multipole는 충돌항 없이 전개된다.

Thomson 계수는 l=0에서 0, l=2에서 0.9, 다른 l에서 1이다. 이는 원본의 unpolarized E2=0 모형이다. 탄성 산란이 monopole에 직접 에너지를 소모시키지 않는 소유권을 유지해야 한다. E/B polarization, ionizing spectrum의 양방향 화학 피드백까지 구현한 것으로 확대하지 않는다.

Lmax=8의 원본 full40 상태는 geometry/clock/thermal 4개와 photon/neutrino energy/number 4×9개다. **nonzero photon Thomson은 photon=neutrino 등식에 기초한 collisionless reduced8 축약을 깨뜨린다.** 새 donor 실행에는 full40을 재사용한다. 기존 D3 ne_source=None 결과는 비교 baseline이며 새 nonzero-ne 문제의 completed receipt가 아니다.

### 기존 ElectronHistory 계열에서 보완할 경계

ElectronHistory는 log(a)에 대한 proper ne의 PCHIP이며 extrapolate=False다. 최소 30행, 유한 값, a>0, 엄격한 증가 a, ne≥0를 검사한다. 하지만 제공된 0을 1e-50으로 올린다. 물리적 0을 보존하는 새 strict adapter를 만든다면 이 차이를 identity에 기록해야 한다. docstring의 SHA-matched 문구와 달리 생성자 자체는 SHA를 검증하지 않으므로 caller가 파일 hash와 scenario를 묶어야 한다.

SmoothElectronHistory는 strictly positive ne만 받으며, uniform log(a) 8193 nodes 위의 natural cubic log(ne) spline이다. 원래 모든 표본에 대한 max/p999 상대 오차를 기록하지만, 스무딩된 표현은 원자료와 byte 또는 표본값 동일성이 아니다. 입력 coverage, interpolation 방식, nodes와 오차를 새 receipt에 저장해야 한다.

## 4. 실제 donor 후보와 정확한 한계

| 후보 | 실제 범위·의미 | z20→2 즉시 소비 가능 |
|---|---|---|
| Original AX08 q=0 full H/He | z20→4; 312,238행; 종별 H/He chemistry와 proper ne | 아니오 |
| B1 R15 dense Q history | z20→4; 16,385행; HII filling factor Q와 bubble 내부 HeII | 아니오 |
| F08 paired electron_density.csv.gz | normal-time 0→10^13 s의 고정 S0 discrete scenario | 아니오 |
| C11 real HHe receiver series | 고정 a=.2, 0→10^12 s chemistry receiver | 아니오 |

### Original AX08 q=0 full H/He

run_hierarchy.py::actual_electrons(owner)가 원래 소비하는 파일:

research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001/history.csv

- SHA256: 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f.
- 312,238행.
- 0부터 센 column4=a, column13=ne_cm3.
- COMPOSITION_RECEIPT.json의 완료 상태, 행수, 파일 SHA를 검증한 뒤 사용.
- source manifest는 original_owner_data_not_uploaded=true라고 명시한다.
- 해당 raw path는 고정 Git tree에 없었다. 독립 scientific review에는 실제 전체312,238행 검사와 endpoint a=.2가 기록되어 있다.

이전 결과의 검토 증거는 재사용할 수 있지만 그 문서만으로 raw 데이터가 현재 로컬에 있다고 가정해서는 안 된다. 이 donor는 prescribed q0 배경에서 계산되었으므로 새로운 D3 backreaction에 넣는 의미는 frozen one-way replay다. 새 D3 geometry가 화학을 다시 바꾸는 양방향 모델이 아니다.

### B1 R15 별도 donor

원본 pin f66929c23ea3fa6e39dd4808e5b27d136c568a03의

research/broad_history_20261010/evidence/RUN002/flrw_n16384/history.npz

이다. 선언된 SHA는 93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4. Dense 파일은 REI_ACCEL01_C02B_FINAL_20261010.zip에 있고 Git에는 257-point preview만 있다고 기존 intake 계약에 명시되어 있다. archive의 Dropbox ID는 id:BSpOijBcT10AAAAAAD3yhw, SHA256은 3d114d3bea604035e2873b804e965605ea8ff9dc06caebe82e5dadfa735e2857다. 이번 조사에서 archive를 다시 다운로드하지 않았다.

ne=(nH+nHe)Q, fixed ionized temperature, Case-B/clumping closure이며 HeIII나 residual electrons 및 전체 H/He temperature evolution이 없다. 원래 full H/He donor와 바꾸어 부를 수 없다. N4 cell-average density도 instantaneous ne(a) 표본과 구별해야 한다.

## 5. 실제 Rust 생성기: 가능한 재사용과 남은 범위 결정

아래 원문을 sources/PR147/ 또는 sources/PR199/에 보존했다.

- rust/rei_microphysics/examples/axbi_reionization.rs: config/output/case와 optional resume CLI.
- src/axbi_driver.rs: DriverConfig, Driver::new, adaptive_step, chemical_stage, output_row.
- src/axbi_sources.rs: AxbiSource::at_redshift, MD14/BB50k 연속 source.
- src/axbi_background.rs: prescribed geometry와 proper clock.
- src/axbi_rates.rs: AxbiProvider::point.
- src/igm_rates.rs: 고정 Grackle3.4.1 Case-A rate literals.
- src/igm_state.rs 및 src/igm_thermal.rs: 종분율, EOS, proper-second reaction/energy RHS.

현재 config parser는 end_zbar를 받지만 validate가 4≤end_zbar<20을 요구하고, source는 4≤z≤20을 요구한다. AxbiBackground 자체는 finite a_end>a_ref를 받는다. 따라서 **단순 endpoint 변경 문제와 물리 source의 허용 범위 변경 문제를 구별해야 한다.**

기존 전체 recipe는 다음과 같다. 초기 z20, xHII=2e-4,xHeII=xHeIII=0, declared adiabatic temperature, zero initial ionizing photons. Proper nH=nH0/a^3,nHe=nHe0/a^3를 쓴다. MD14 SFR, Zstar=.002의 ionizing yield, fesc=.2, normalized BB50k13.6–100eV 방출을 쓴다. Grackle3.4.1 selected Case-A CI/RR/DR, cooling 및 CMB Compton을 포함한다. Clumping=1, AGN/CR/HH/RCT는 끈 조건부 모델이다. 온도 operational domain은 [1,10^6] K다. 이 범위를 물리적 정확도 인증으로 해석하지 않는다.

full z2 donor가 새로 필요하면 다음 순서가 구체적이다.

1. HE31의 새 source/scenario ID로 [2,20]에서 쓸 emissivity, spectrum, chemistry와 IC를 명시한다. 원래 [4,20] scenario는 그대로 보존한다.
2. 기존 Rust driver·provider를 별도 단위로 파생하거나 새 explicit domain parameter를 갖춘 wrapper로 구현한다. 원본 frozen 자료를 새 scenario의 검증 결과로 바꾸어 표시하지 않는다.
3. 실제 새 ne(a) 결과를 생성하거나 기존 fullinterval source의 원자료를 확보한다. ne=nH xHII+nHe(xHeII+2xHeIII), proper density, endpoint, 단위와 source hash를 결속한다.
4. 그 frozen donor를 full40 ne_source에 전달한다. 결과를 one-way prescribed-chemistry-to-Einstein/Thomson coupling으로 명시한다.

기존 CLI 형태는 다음과 같다. 이 명령은 현 원본 계약상 end_zbar≥4에서만 유효하며, 이번 조사에서는 실행하지 않았다.

```sh
cargo run --release --manifest-path rust/rei_microphysics/Cargo.toml \
  --example axbi_reionization -- \
  --config CONFIG --output NEW_DIR --case CASE_ID
```

이 디렉터리에 저장한 source subset은 조사용이다. 전체 crate 및 필요한 모든 cross-section/provider 파일을 완전히 vendor한 빌드 산출물이라고 표시하지 않는다.

## 6. 가속·runner 재사용

ACCEL02 source pin은 231df3ab717dbc112f63b77953f64def08e9bcb5, 파일은 research/rei_sigma_pi_native_moments_20261021/moments.cpp다. 원래96×32 quadrature의 반사쌍을96×16으로 합치고 세 moments를 한 번에 계산한다. 이는 C15 warm source의 exact pairing이다. 새로운16-point Gauss rule을 대입한 것이 아니다. D3 canonical FV2592 packet kernel와 입력계약이 다르므로 직접 바꿔 끼울 수 없다. immutable context와 exact symmetry reduction 설계는 참고할 수 있다.

HE30 shared_runner.py의 shared case identity lock, CPU lease, dynamic refill, reserve/memory/load 계산은 새 단위에서도 재사용할 수 있다. 별도 물리 module이 donor hash·scenario·model source·parameter 및 numerical controls를 case identity에 포함해야 한다. HE30 completed-only adapter의 기존 완료 결과가 새 Thomson 문제의 완료로 판정되지 않도록 한다. 이번 조사에서는 runner나 원본 파일을 수정하지 않았다.

속도 배수나 NCP에서의 실제 가속 정도를 측정하지 않았다. native coefficient/evaluation 수 감소는 구현상 구조이고 measured wall-time speedup과 다르다.

## 7. 재배포와 근거 범위

REI root와 Rust package는 MIT이며 LICENSE를 보존했다. igm_rates는 Grackle3.4.1 af7939494ce65007887ada7b98d1813df6843346의 선택된 rate_functions.c literal port다. 원문 주석과 tests/data/igm_grackle/LICENSE의 Enzo/Grackle notices를 유지해야 한다. 이것을 upstream Grackle 라이브러리를 직접 실행한 결과와 동일하다고 기술하지 않는다.

정확한 URL, pin, source 경로, donor hash 및 observed limits는 SOURCE_REUSE.json에, PR list/delta는 UPSTREAM_DELTA.json에 있다. SOURCE_FILE_HASHES.json은 저장된 조사 사본 자체의 SHA256·Git blob SHA1을 구분해 기록한다. 이 조사만으로 새로운 z2 donor나 coupled 결과가 완료되었다는 주장은 하지 않는다.

