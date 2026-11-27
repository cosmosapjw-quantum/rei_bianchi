# HE-EXP-DRIFT-02 구현 독립 검토 — 최초 실행 전

검토 기준: BASS_HE HEAD `ac6042a6b0610b09d0576538767ee0299389a5eb`에서 작성 중인 `research/program_expansion_20261025/continuation_20261027/`. 현재 root AGENTS.md를 읽었다. 기존 HE101/INTAKE01 source·failure·budget·C8 기록은 수정하지 않았다. 이 검토는 source read와 독립 Gaussian 유도 대조이며 **테스트를 실행하지 않았다**.

검토자는 새 코드 작성자가 아니다. 독립 Gaussian derivation 및 polynomial expected values를 먼저 작성한 후 root의 `finite_drift.py`와 별도 작성자의 `source_diagnostic.py`를 읽었다. 코드 검토의 독립성과 이론 원문 저작을 구분한다. 최종 실행 결과·게시·백업은 아직 이 검토의 근거가 아니다.

## 검토한 identity

| 경로(새 단위 상대 경로) | SHA-256 |
|---|---|
| `src/finite_drift.py` | `693315a21effe9bf55a8a3255c7a6ca7280385f459606bd2fb3fad27f3054763` |
| `src/source_diagnostic.py` | `0c15527d5ed88a542688f871007b15a34726713dfef9cacb50145352f04d1018` |
| `tests/test_finite_drift.py` | `3c202b7e191415fb6be89c283a022008a35bfb5be310f6b32263e443fa1d38dc` |
| `tests/test_source_diagnostic.py` | `a6790dc18dbdb938a2e0a28d0b189ac9d1e16ec27f7bfcce9a82df812182734f` |
| `run_validation.py` | `4c9797c7d89291aa37f87059ab5d506d2c0aa8bf42616c326f51a21dd1ed7260` |
| `VALIDATION_CONTRACT.json` | `13c70d38c7110df3056f2546198c203999951e06ef0b846cd4d1d4284febacd1` |

상속된 `continuation_20261025/run_validation.py`, `pair_source/h_he_intake.py`, `exchange/exchange_closure.py` 및 source evaluator/input pin의 실제 사용도 읽었다. 아래 finding은 위 새 파일 snapshot에 적용한다.

## 채택한 식–코드 대응

1. `T_star`, reduced mass, 선형 `K`, 0차 `G(Tb-Ta)`는 byte-pinned 기존 adapter에서 얻는다. 완료된 HE101 과학 suite를 호출하지 않는다.
2. `beta=ab(Ta-Tb)/Tstar`, `zeta=5/2-3 Q12/Q11`, `delta Qa=K U²(b+beta zeta)`, `delta Qb=K U²(a-beta zeta)`는 Gaussian 원 적분에서 얻은 식과 일치한다.
3. `R_a=-KU`, `R_b=-R_a`, `E_s=Q_s+u_s dot R_s`의 raw/centered 부호가 맞다. `K U²`는 diagnostic total로 반환되고 다시 heat에 가산되지 않는다.
4. 각 종의 온도 RHS는 단일 thermal population의 `3 n k_B/2`를 사용한다. 두 종의 common-T를 선언하지 않는다. Elastic count, binding, nonthermal source를 0으로 보존한다.
5. `maximum_drift_ratio`는 caller의 Taylor domain이며 오차 certificate로 보고하지 않는다. `physical_provider_admitted=false`, `remainder_bound_certified=false`, source uncertainty null이 유지된다.
6. Source diagnostic의 `dQ/dlnT`는 Bruno quotient의 analytic derivative와 일치한다. `sigmoid(z)*sigmoid(-z)` 사용은 saturated tail에서 `1-sigmoid(z)`의 cancellation을 피한다.
7. 원 source 온도는 20000 K 한 점으로 제한된다. 다른 온도에서 사용하는 coefficient tests는 명시적인 합성 coefficient다. Independent Decimal60 quotient oracle, gamma-integral/polynomial Gaussian control은 새 구현 자체의 출력을 다시 expected값으로 쓰지 않는다.

위 항목은 **source-reviewed/derived correspondence**이며 실제 실행 성공을 뜻하지 않는다.

## 수정 finding

### DRIFT02-R1 — 실행 기록이 새 구현 바이트를 포함하지 않음

- 분류: 구현·재현성; 우선순위 P1.
- 대상: 새 `run_validation.py`가 상속 runner를 `scope="tests"`로 호출하는 부분, 상속 runner의 `inputs` 구축.
- 관찰: 상속 runner의 `source_sha256`는 `ROOT/tests/**`와 `ROOT/sources/**`만 수집한다. 새 구현은 `ROOT/src/**`에 있으므로 현재 START에는 `finite_drift.py`, `source_diagnostic.py`가 묶이지 않는다. `runner_sha256`는 상속 모듈의 `__file__`을 해시하므로 새 wrapper identity도 빠진다.
- 영향: 성공 로그만으로 실행 당시 새 code identity를 재현할 수 없다. 나중에 같은 test가 남고 `src`가 바뀌면 단위 테스트 결과와 implementation version의 연결이 불명확해진다.
- 최소 교정: 원 runner를 보존하고 새 wrapper가 START 전에 새 `src`, wrapper, 필요한 inherited source/input의 실제 SHA manifest를 작성해 `sources/`에 포함시키거나 START에 해당 identity를 추가한다. 최초 실행 후 START/FINISH에 manifest 또는 각 실제 source가 포함됐는지 확인한다.
- 종료 근거: 실행 receipt에 새 `src`와 wrapper/상속 의존성 identity가 연결되고 실제 바이트와 일치해야 한다.

### DRIFT02-R2 — binary64 변환 overflow가 정해진 입력 오류 경계를 벗어남

- 분류: 구현 입력 검사; 우선순위 P2.
- 대상: 새 `finite_drift._finite` 및 inherited pair adapter를 호출하기 전의 숫자 검사.
- 관찰: `_finite`는 `float(value)`의 `OverflowError`를 잡지 않는다. `10**400`은 `numbers.Real`이지만 binary64 변환에서 예외가 발생한다. Inherited pair adapter도 새 wrapper의 사전정규화 없이 먼저 호출되므로 temperature/mass/density의 동일 입력에서 `math.isfinite` 경유 overflow가 드러난다.
- 영향: 문서화된 finite-real rejection이 일관된 `ValueError`로 반환되지 않는다. `source_diagnostic`은 같은 경계를 이미 명시적으로 처리한다.
- 최소 교정: 새 wrapper의 `_finite`에서 변환 overflow를 `ValueError`로 바꾸고, inherited 함수에 넘길 새 public API 숫자들을 유한한 binary64 값으로 먼저 정규화한다. 기존 파일은 수정할 필요가 없다.
- 검증: 새 API의 `q12`, `mass`, `temperature`, `density`, velocity component 등에 `10**400`을 넣는 targeted rejection을 추가한다. Bool/string/NaN/Inf 검사와 구분해 binary64 representability 오류로 확인한다.

### DRIFT02-R3 — 이론과 diagnostic residual의 부호 대응을 명시해야 함

- 분류: convention/출력 계약; 우선순위 P2.
- 대상: THEORY 식(22)–(23), `source_diagnostic.same_law_residual`, 반환 metadata.
- 관찰: 이론의 `D=3(r-1)-slope`에 대해 코드의 `same_law_residual=slope-3(r-1)=-D`다. 둘 다 유효한 정의지만 현재 반환에는 그 부호 정의가 별도 필드로 없다.
- 영향: 이론의 식(23)을 code residual에 그대로 대입하면 row-based minus derivative-based species heat의 부호가 뒤집힌다.
- 최소 교정: 부호를 통일하거나 반환에 `residual_definition="slope - 3*(ratio-1) = -D_theory"`를 추가한다. 현재 code convention을 유지하면 `Qa_row-Qa_derivative=+K beta residual U²`, He는 그 음수라는 대응을 명시한다.
- 종료 근거: machine-readable definition, 이론 대응, synthetic residual sign test가 같은 convention을 사용한다. 이 residual을 physical uncertainty로 해석하지 않는 기존 경계는 유지한다.

### DRIFT02-R4 — 양의 quadratic dissipation이 0으로 underflow하는 경로

- 분류: 수치 representability; 우선순위 P2.
- 대상: `dissipated=k*u2` 뒤의 검사.
- 관찰: 코드가 nonzero `U²`, drift ratio 및 force의 underflow를 거부하지만 `k>0,U²>0,kU²==0`는 거부하지 않는다. 예를 들어 현재 synthetic scale에서 `U=(1e-150,0,0)`이면 `U²`와 `U²/s²`는 representable하고 force는 nonzero지만 `kU²`는 binary64에서 0이 될 수 있다. 이는 아직 실행하지 않은 정적 반례 구성이다.
- 영향: 열원 precision failure를 zero dissipation으로 조용히 반환한다. 현재 API의 다른 nonzero-underflow 경계와 불일치한다.
- 최소 교정: `k>0 and u2>0 and dissipated==0`이면 representability `ValueError`를 반환하거나 명시적인 underflow 상태를 반환한다. 현재 예외 중심 API에는 전자가 작다.
- 검증: equal-T로 0차 heat를 제거한 새 targeted fixture에서 `U²`/drift²/force는 살아 있고 dissipation만 underflow하는 입력을 검사한다.

## 다음 판정

핵심 수식, 단일 energy ownership, source/scientific admission 분리는 현재 snapshot에서 일치한다. 위 네 finding을 수정한 변경만 재검토한 뒤 최초 bounded test로 진행할 수 있다. 기존 suite/HE101을 추가 실행할 근거는 없다. 실제 test log와 source SHA binding 확인이 끝나기 전에는 implementation PASS를 부여하지 않는다.

작업 범위 밖의 untracked `research/he27_sourcecut_native_20261016/results/fast_reference_dop853/.native.jsonl.gz.oS4pua`를 관찰했으며 읽기·수정·삭제하지 않았다.

## 최초 실행 전 수정 확인

Root가 네 지적을 반영한 변경 부분만 다시 읽었다. 별도 테스트 실행은 하지 않았다.

| 수정 파일 | 확인한 SHA-256 |
|---|---|
| `src/finite_drift.py` | `90a66fc03cd2a4020e97dab99de9559ad5a426fc3dab2200652682bfd9df823e` |
| `src/source_diagnostic.py` | `5cce7ae4f5b9c9ee15239f18b71f6bc065abfec90e2c45b91011af0aba8b3785` |
| `tests/test_finite_drift.py` | `9a9953b6395346b6bcd494a75d9c307a5ea76b96898eb726d83176daf75936ed` |
| `run_validation.py` | `aca8bb5ecd1f6f73f08b18d6835899646ecd39816ee1b8805470599b17cd18d1` |
| `THEORY_KO.md` | `4bae79c9f4960419192a23d56aac5c797f84758c960cd37ed6be32660e0bce7d` |

- R1: 새 wrapper가 source/test/wrapper/contract 및 baseline dependencies의 실제 byte identity를 `sources/TESTED_DEPENDENCIES_<sequence>.json`에 기록한다. 원 runner의 `sources/` 해시 수집 경로에 연결되므로 코드 수준 교정은 확인했다. 실제 START/FINISH binding은 최초 실행 후 확인할 항목이다.
- R2: `_finite`의 binary64 변환 exception 정규화 및 8개 inherited 입력의 사전정규화를 확인했다. Huge-int temperature/mass/density rejection control이 새 테스트에 포함됐다.
- R3: 현재 게시 대상 THEORY는 `D=slope-3(r-1)`로 통일했으며 `Qa_row-Qa_derivative=+K beta D U²`다. 반환 `residual_definition`과 heat coefficient 문자열도 같은 부호다. 이 reviewer의 최초 유도 snapshot은 이전 `D` 정의를 사용한 역사적 파일로 남기고, repo THEORY의 현재 정의를 사용한다.
- R4: 양의 `k,U²`에서 `kU²==0`을 거부하는 guard 및 dissipation-only underflow counterexample test를 확인했다.

판정: 네 finding의 코드 교정은 확인됐고 **최초 bounded validation으로 진행할 수 있다**. 추가 source review를 요구하지 않는다. 최종 실행 evidence 검토는 해당 test 로그와 START/FINISH에 한정한다. implementation PASS와 physical provider admission은 각각 실제 실행 결과와 열린 물리 입력 상태에 따라 별도로 판정한다.

## 추가된 neutral mass converter의 최초 실행 전 검토

Root의 별도 지시로 새 `src/mass_binding.py`와 `tests/test_mass_binding.py` 및 실제 packet-to-WU mapping만 읽었다. 이전 네 finding은 다시 열지 않았다. 이 검토에서도 테스트는 실행하지 않았다.

| 대상 | 확인한 SHA-256 |
|---|---|
| `src/mass_binding.py` 초기판 | `665a7cc34a452e3bbb106828a06755470348add672a74f84b2ca2028efdb50bc` |
| `tests/test_mass_binding.py` 초기판 | `a425eff371a54f7f0363f1f2e60f3e35412678e8d21b065f26200a4fbf84cabd` |
| `sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json` | `847fa2f0bf0f0826d1b5bea69250ac4892cf25d063aaf8afe12257729982487b` |
| `sources/raw/WU_R1_species.json` | `a18052f6db432192e1e0d4c75f8f2d49c71f3a5eb7cac206e7bc445fec2e8f80` |

실제 packet의 선택 행은 다음 WU compiler record와 일치한다.

| source row | WU ID | 고정된 neutral identity |
|---|---|---|
| `NIST_AME2012_H1_NEUTRAL_GROUND` | `sp_7b3d2e472131e6c645d7` | Z=1,A=1,isomer=ground,count=1; q=0; 1s_ground; material |
| `NIST_AME2012_HE4_NEUTRAL_GROUND` | `sp_17efcd73203997543678` | Z=2,A=4,isomer=ground,count=1; q=0; electronic_ground; material |

`m=Ar*m_u`, 불확실성 민감도 `m_u*u(Ar)` 및 `Ar*u(m_u)`를 별도로 반환하는 산식은 맞다. covariance 부재에서 표준불확실성을 자동 합성하지 않으며, neutral-atom rest mass에 전자/nuclear binding을 다시 더하지 않는다. 원 NIST HTTP bytes가 없다는 상태와 mixed-vintage field를 유지한다. 이 검토는 NIST 원문을 새로 취득한 주장이 아니라 packet의 식·identity·소비자 대응 검토다.

### DRIFT02-R5 — source row와 정확한 isotope ID의 일대일 binding

- 분류: 물리 입력 identity/구현; 우선순위 P1.
- 관찰: 초기 converter는 row count=2와 `only_two_neutral_ground_ids=true`를 검사하지만, 실제 허용되는 두 species/source ID를 제한하지 않는다. H1 행의 `wu_species_id`와 composition만 D-neutral `sp_e122664dacbd50a873e3`, Z=1,A=2로 바꾸면 원 H1의 Ar/NIST source_ref와 함께 통과할 수 있다. WU에는 실제 해당 D-neutral row가 있다.
- 영향: neutral/ground라는 부분 identity는 맞으나 source mass를 잘못된 isotope에 배정할 수 있다.
- 최소 교정: 정확한 두 WU ID와 source row ID/source_ref의 대응을 고정하고 선택 set이 그 pair와 일치하는지 검사한다. Wrong-isotope substitution을 거부하는 targeted control을 추가한다.

### DRIFT02-R6 — binary64 mass 출력의 유한성

- 분류: 수치 입력/출력 contract; 우선순위 P2.
- 관찰: 양의 finite Decimal `Ar='1e400'`은 Decimal product가 유한하더라도 `float(mass)`가 infinity가 될 수 있다. 초기 converter는 binary64 출력이 양의 유한 값인지 검사하지 않는다.
- 최소 교정: binary64 변환 결과의 finite/positive를 검사하고 unrepresentable 값은 명시적으로 거부한다. 정상 source packet의 exact rational multiplication oracle은 그대로 유지한다.

위 두 항목은 실제 source 행의 정확성을 부정하는 finding이 아니다. 새 consumer가 선언한 exact-pair/finite-output contract를 입력 변경에도 유지하도록 하는 교정이다. 완료되면 최초 실행의 해당 새 controls와 receipt만 확인한다.

Root의 수정 후 `mass_binding.py` SHA-256 `36b8654622db002d677c95a78d08f397ee3fe0e3cc7ab38ccf1f78ef5735d3fd`, `test_mass_binding.py` SHA-256 `34aeaea9cbb5afa0c230853c1567998c5acfd40c35ac66e7d85d0da83d2022a7`를 실제로 읽었다. 정확한 두 ID와 `(NIST row ID, source_ref)` 대응표, 최종 pair set 검사, 양의 유한 binary64 mass 검사를 확인했다. D-neutral substitution과 `1e400`/`1e-400` 거부 control도 준비되어 있다. R5/R6의 코드 교정은 닫혔으며 새 mass 범위를 포함한 **최초 bounded validation으로 진행할 수 있다**. 실제 실행 결과는 여전히 부모 runner의 로그를 기다리는 상태다.
