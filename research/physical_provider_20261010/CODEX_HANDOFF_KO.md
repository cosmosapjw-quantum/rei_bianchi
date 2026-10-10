# Codex 인계 프롬프트 — REI-PHYSINPUT-01

`cosmosapjw-quantum/rei_bianchi`의 새 물리 입력 연구 결과를 이어받아 **production consumer에 명시적인 source-backed conditional 실행 경로를 연결**해줘. 사용자는 이론→코딩 연구 루프, 관련 저장소 수정 및 결과 push를 승인했다. 기존 작업을 손상시키지 않도록 현재 원격 상태를 읽고 새 isolated branch/worktree에서 진행해. 자동 merge는 하지 마.

현재 전달 branch는 `research/physical-provider-20261010`, 연구 폴더는 `research/physical_provider_20261010/`다. 최초 기준은 PR93의 `17bd1cc0ce1484ee61cac60ab1bda207ae264381` / tree `9966709d24423056df5d9821391b2316530ca561`. 원격 branch와 publication receipt에서 실제 최신 commit/tree를 읽어 pin해. `main`을 최신 개발 기준이라고 가정하지 마. 보고서가 작성된 뒤 다른 개발이 진행됐으면 source identity로 차이를 구분해.

## 먼저 읽을 것

1. `REPORT_KO.md`, `CONTRACT.json`, `RESEARCH_DAG.json`, `independent_review.json`.
2. `THEORY_DERIVATION_KO.md`의 정의·source Jacobian·closure·D01만 필요한 만큼.
3. `SOURCE_MANIFEST.json`, `evidence/VALIDATION.json`, `evidence/extended.json`, `evidence/input_audit.json`.
4. `run_interval.py`, `background.py`, `hm12_data.py`, `native/NATIVE.md`, `native/src/main.rs` 및 실제 production `axisym_contract.rs` / `axisym_coupling.rs`.

Astra용 PHYS–MATH research/coding harness v4.0.0을 적용해. 선택 근거는 사용자 명시 지시다. 패키지 이름으로 실제 runtime 모델이 바뀌었다고 주장하지 마.

- Research ZIP SHA256: `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`, stable ID `libfile_07a54bff29548191bb87edd4bbe9cc73`.
- Coding ZIP SHA256: `dc99e7ab2f9629dcce3ec0758d97e19acc5b645f86e208d1b338bb6430ff8d7a`, stable ID `libfile_b1f31b28c0688191a06a4ae8f943d862`.

접근 가능한 동일 해시 패키지의 START_HERE/core/state를 읽어. 배포 state의 NOT_RUN 템플릿은 실행 이력이 아니다. 하네스에 접근하지 못하면 HARNESS_UNAVAILABLE을 기록하고 본 프롬프트의 이미 허용된 읽기·source 복구를 먼저 진행해. 과거 기억으로 하네스를 복원하지 마.

## 이미 완료된 범위 — 반복 감사 대신 재사용

- 원저자 HM12 `emissivity.out`과 `UVB.out` bytes를 취득해 고정했다. UVB의 unequal duplicate wavelength19쌍은 점프로 보존한다. Source는 emissivity, 최초 photon IC만 UVB다. 이후 $J_\nu(z)$나 $\Gamma(z)$를 덮어쓰지 않는다.
- Exact Einstein dust+Λ LRS Bianchi-I, nonzero $s_i/H_i=0.001$, $z_i=5.807$, $b_i=0$, proper-time map, density normalization을 구현했다. `z`는 volume label이다.
- $T_i=50000K$, charge-neutral local ionic equilibrium의 유일 root를 구했다. 이것은 선택한 warm-parcel IC이며 REC/관측 IC가 아니다.
- 기존 FT03 RR/CI/DR와 Verner cross sections를 실제 호출하고 기존 AXI derivative로 SI conversion, dilution, thermal-particle correction, shear work를 검증했다.
- 초기 momentum $q=E_i\in[10,50000]$ eV의 2904-node 첫 coupled interval $0..10^{11}s$를 실행했다. 전체 상태는 `extended_dataset.npz`. 총11개 history의 범위와 수치는 validation에 있다. 기존 별도 물리 history는 `HOLD`다.
- 원래200eV 상한의 HeII heating53.945% 누락을 발견해50keV까지 확장했다. 원 실패·차이를 보존한다. 더 높은 반응율은 fit domain 밖이므로 외삽하지 않는다.
- 10 intake +6 native +27 기존 영향 범위 tests PASS; 시간법 비교와 discrete refinement PASS_SCOPED. 독립 원자물리/continuum/global validation이 아니다.

## 다음 bounded work unit: P01 production conditional consumer

1. 현행 production runner의 time/geometry/provider 소유권을 확인하고 **별도 `SourceBoundConditional` 또는 동등하게 구분되는 실제 실행 계약**을 추가해. 기존 `AxisymRunContract::PhysicalHistory`는 metadata를 채워도 `PhysicalExecutionNotImplemented`인 상태다. 이를 무조건 통과시키거나 Case-A escape를 `CaseAExplicitDiffuse`/`FullCoupledOts`로 표시하면 안 된다.
2. 이 연구의 frozen source bytes·background·IC·closure를 읽는 provider를 연결하고 최소 한 실제 production coupled interval을 동일 입력/동일 시간좌표에서 실행해. Research executable만 다시 실행하는 것으로 production integration을 완료 처리하지 마.
3. 상태·source·opacity가 같은 stage를 소비하는지 확인해. `N_rel=a_rel^3 n`, $E=qR$, 방향 Jacobian $R^{-3}$, thermal energy와 binding 분리, recombination escape ENERGY만 기록하는 의미를 유지해. 방출 광자수는 미정이다.
4. 원래 FT03 guard30000..110000K, Verner E≤50000eV, optional CR/RCT/HH OFF, 기존 F04/F08 tolerance 및 과거 FAIL을 보존해. 성능·단계 편의를 위한 clipping/fallback/threshold 변경은 금지다.
5. 기존 연구 결과와 같은17개 epoch의 state/observable·photon/energy ledger를 비교해. Consumer integration이 바꾼 부분에만 targeted test와 독립 review를 수행해. 실제 code path, exact source SHA, 명령·exit, 최초 failure·수정을 보존해.

### Acceptance / stop condition

Production의 실제 경로에서 source-hash-bound 첫 interval이 실행되고, 온도·양성·정규화·반응 회계·해당 discretization 오차가 계약을 만족하며 독립 reviewer가 scoped use를 승인하면 P01을 닫아. 다음 과학 질문에 필요한 gate로 넘어가고 같은 부재 검색을 반복하지 마. 실행 경로 또는 실제 dataset 접근이 없으면 정확한 blocker와 최소 다음 조치만 남겨.

## 물리 후속 분기

원 목표가 차가운 mean-IGM/REC→REI라면 P02: source-pinned REC IC 및 low-temperature atomic/thermal provider가 먼저다. 따뜻한 모델을 몰래 저온 모델로 바꾸지 마. Full photon history라면 P03: diffuse/OTS, secondary·Compton, high-energy boundary 및 model-error 계약을 먼저 정해야 한다. 현 자료만으로 full physical/global EoR admission이나 $Q_V$, 관측 재현을 주장하지 마. 장기 history는 실제 error budget과 source/atomic domain을 닫은 뒤 수행해.

## 재현 필요시

Python3.12, numpy2.3.5, scipy1.17.0 및 Rust1.99.0으로 실행했다. Native crate는 외부 Cargo dependency가 없다. manifest/source hash를 먼저 확인하고, 코드가 그대로면 반복 full science 재실행 없이 필요한 smoke/새 consumer 비교만 수행해.

```bash
python3 -m pip install -r research/physical_provider_20261010/requirements.txt
cargo build --release --locked --manifest-path research/physical_provider_20261010/native/Cargo.toml
python3 research/physical_provider_20261010/run_interval.py --emax 50000 --tag consumer_reference
```

전체 재생산은 `bash research/physical_provider_20261010/reproduce.sh`. 이는 기존 evidence 파일을 다시 쓰므로 새 worktree 또는 출력 복사본에서 실행해. Native target binary는 Git에 넣지 않는다. 저장된 source bytes를 사용하며 실행 때 최신 외부 표로 바꾸지 않는다.

완료하면 한국어 보고서, machine-readable DAG/validation/반환 identity, 다음 최소 work unit을 갱신하고 새 branch에 non-force push해. 원격 ACK/commit/tree 확인을 과학 validation 또는 remote byte restore와 혼동하지 마. 필요 없는 전체 재다운로드·재검증·리뷰의 리뷰는 하지 마.
