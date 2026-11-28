# HE-EXP-DRIFT-02 최종 독립 검토

## 판정

**APPROVED_SCOPED_IMPLEMENTATION / pass_scoped.** 고정된 조건부 H–He Maxwell 모델의 drift 1차 force·2차 centered heat, 20000 K source-row diagnostic, 두 neutral-isotope mass의 소비자 변환에 대해 유도–구현–독립 기대값–실제 실행 연결을 확인했다. 실행 전 지적 여섯 건은 수정됐으며, 해당 변경을 포함한 한 번의 bounded 실행에서 24개 method가 모두 성공했다. 추가 테스트는 필요하지 않다.

물리 공급자 admission, full differential law, isotope-dependent transport accuracy, calibrated source uncertainty와 finite-drift remainder bound는 열린 입력 상태를 유지한다. 이 검토로 WU registry/physical admission이나 HE101 C8을 변경하지 않는다.

## 검토 독립성과 범위

검토자는 새 구현을 작성하지 않았다. 기존 PR102 원문을 읽고 Gaussian conditional expectation과 polynomial exact controls를 독립적으로 유도한 다음, root/별도 작성자의 code와 test를 대조했다. 첫 실행은 root runner가 수행했다. 검토자는 그 테스트를 다시 실행하지 않고 실제 START, FINISH, stdout, stderr, ledger와 입력 바이트의 identity를 확인했다.

검토 파일: `src/finite_drift.py`, `src/source_diagnostic.py`, `src/mass_binding.py`, 대응 세 test 파일, 새 wrapper와 byte-pinned inherited runner, 실제 선택 source/mass packet. All-target consumer projection의 별도 구현 전체를 이 검토의 scientific approval에 포함하지 않는다.

## 실제 실행 근거

단위 경로: `research/program_expansion_20261025/continuation_20261027/`.
불변 출발 HEAD: `ac6042a6b0610b09d0576538767ee0299389a5eb`.
실행: `evidence/validation/01_tests/`.

| 항목 | 실제 확인값 |
|---|---|
| 실행 상태 | STARTED 원기록 보존; FINISH PASS |
| 종료 코드 | 0 |
| method | 24개의 개별 `ok` 및 `Ran 24 tests ... OK` |
| 실행 횟수 / repair | 1 / 0 |
| 측정 CPU | 0.14653116 s = child 0.144607 + parent 0.00192416 |
| 측정 wall | 0.14577179600019008 s |
| allocation | 4 CPU s / 15 wall s; overshoot=false |
| source temperatures | 실제 H–He source 20000 K 한 점 |
| HE101 START / historical suite replay / physical campaign START | 0 / 0 / 0 |

이 비용은 runner가 명시한 measured validation interval이다. 준비·모델·네트워크·파일 IO의 전체 비용을 이 값에 포함했다고 주장하지 않는다. 그 항목의 `UNKNOWN_NOT_ZERO`와 `end_to_end_cap_claimed=false`가 ledger에 보존돼 있다.

## 실행 바이트와 출력 연결

START와 FINISH의 source identity map은 동일하다. 직접 계산한 SHA-256으로 START의 **29개 source/test 항목 전체**가 현재 저장 바이트와 일치함을 확인했다. `sources/TESTED_DEPENDENCIES_01.json`의 **17개 dependency 항목 전체**에 대해 SHA-256과 size가 일치했다. 불일치는 0이다. 새 source 세 파일과 wrapper 및 inherited dependencies가 이 manifest에 연결되어 초기 R1을 닫았다.

| 실행된 새 source | SHA-256 |
|---|---|
| `src/finite_drift.py` | `90a66fc03cd2a4020e97dab99de9559ad5a426fc3dab2200652682bfd9df823e` |
| `src/source_diagnostic.py` | `5cce7ae4f5b9c9ee15239f18b71f6bc065abfec90e2c45b91011af0aba8b3785` |
| `src/mass_binding.py` | `36b8654622db002d677c95a78d08f397ee3fe0e3cc7ab38ccf1f78ef5735d3fd` |
| tested dependency manifest | `06a60f870dca0753bd7ec3d7ef53229120f69f9514f77f6becde9a5ee2575789` |
| stdout | `168156801df2a1bf9a4dff164f7dec23bfd8d7da2334066fed1b0ee3b09ea47f` |
| stderr | `068cf9c79ff8d4912de5105e80dc1e5423b7b77c5c9b694802210aa7e5cce39d` |

`evidence/SOURCE_DIAGNOSTIC.json`과 `evidence/NEUTRAL_MASS_CONVERSION.json`은 실제 stdout의 각 JSON 객체와 구조적으로 동일하다. 출력 파일을 만들기 위해 source evaluator를 다시 실행한 흔적을 요구하거나 그러한 재실행을 수행하지 않았다. 이 identity 검토의 기계 기록은 함께 제공한 `INDEPENDENT_REVIEW_FINAL.json`이다.

## 과학·수치 판정

1. **Finite-mass same-event heat — derived + implementation-verified.** `Qa+Qb=K U²`, `Ra=-K U`, `Es=Qs+us dot Rs`가 같은 truncation order에서 일치한다. Particle count, binding, nonthermal energy를 열원으로 중복 가산하지 않는다. Signed quadratic temperature-exchange correction을 clamp하지 않는다.
2. **독립 controls — numerically checked.** `sigma1=Lambda/g`의 정확한 Gaussian 평균 및 `sigma1=Lambda*g`의 정확한 cubic-force/quartic-heat residual을 사용했다. Half-drift에서 각각 1/8, 1/16 scaling control이 성공했다. Galilean transformation, species interchange, equal-temperature mass partition, source/thermal-count boundary 및 입력 representability controls가 성공했다.
3. **Actual source-row diagnostic — numerically checked at one point.** 20000 K에서 저장 Q11과 inherited evaluator의 차이는 0이다. Q11=`2.8378312527861555e-20 m²`, Q12=`2.229085677933474e-20 m²`, ratio=`0.7854891568147256`, log slope=`-0.6334468971263719`다. `D=slope-3(ratio-1)=0.010085632429451152`는 독립 Decimal60 quotient oracle과 일치했다. 이 값은 두 fit의 row identity discrepancy이며 physical calibrated uncertainty가 아니다.
4. **Neutral mass conversion — source-field conditional + implementation-verified.** WU의 정확한 H1 neutral `sp_7b3d2e472131e6c645d7`와 He4 neutral `sp_17efcd73203997543678`에만 선택 source row를 연결한다. H1 mass=`1.6735328406534731912916e-27 kg`, He4 mass=`6.6464790808691923446396e-27 kg`는 quoted Ar와 m_u의 exact-rational oracle로 확인됐다. D substitution, bare/excited/nonmaterial alias, invalid decimal 및 binary64 overflow/underflow를 거부했다. Joint covariance는 미확보로 남고 불확실성을 임의 합성하지 않는다.

Source packet은 primary-page field transcription으로 기록돼 있다. NIST HTTP 403과 raw-byte 미확보 상태를 이 검토로 raw-byte verification으로 바꾸지 않는다. Neutral mass identity와 elemental H–He collision fit의 isotope accuracy는 서로 다른 의무다.

## Finding 종료와 유지할 gate

R1 실행 source identity, R2 overflow 입력 오류 경계, R3 residual 부호 대응, R4 dissipation underflow, R5 exact isotope/source-row binding, R6 binary64 mass 출력 검사가 수정 후 해당 method 실행으로 닫혔다. 잔여 blocking implementation finding은 없다.

유지하는 gate: `physical_provider_admitted=false`, `source_calibrated_uncertainty=null`, `remainder_bound_certified=false`, full differential/angle law 미승인, 글로벌 물리 완료율 null 및 L4 false. 원 HE101 `C8=PARTIAL_EXPORT`, 19/20, repair reserve0, 실제 PASS/FAIL/FAIL 및 원 예산을 보존한다. 게시와 이중 백업은 root의 별도 실제 provider/commit receipt로 판정한다.
