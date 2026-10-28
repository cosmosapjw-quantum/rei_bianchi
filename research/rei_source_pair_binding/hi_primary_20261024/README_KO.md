# 선택 elemental-HI source pair: 정적 구현 준비

**상태: STATIC_PREPARED_UNEXECUTED. L1 수치/source admission은 발행되지 않았다.**

이 디렉터리는 고정된 C23B z=2.479 elemental ground-state HI summary를 Href당 여섯 에너지 소유자 및 입자 장부에 연결한다. 원료는 `source_card.json`에 원본 선택 row의 바이트 그대로 보존했다. 원본 과학 commit은 `54477b285e0c712610453bca1408a076af43521d`, 실제 읽은 commit은 `b8882d026887f375acf90768d4e3740eb03da226`, CASES blob은 `61bcbc0b44206f496534da6bdffcdfe1731ad063`이다. 원본 경로와 각 파일 SHA-256은 `SOURCE_BINDING.json`에 기록한다.

## 선택 범위와 해석

고정 채널은 elemental HI이며 H1/D/T를 식별하지 않는다. 문턱은 공급자의 13.6 eV, photon support는 [13.6, 50000] eV, frame은 `bath_frame_rest_target`, recoil은 zero approximation이다. 정규화는 target당 proper-second이며 x_hi는 고정 Href당 흡수 target 수다. 실제 채택 진폭은 amplitude=1이다. 다른 진폭에 대한 선형 민감도를 제공한다는 것이 새로운 source calibration을 뜻하지 않는다.

선택 동역학은 `NO_DEPOSITION_SELECTED_MODEL`이다. RR, feed, deposition, secondary reactions, 수송, finite-stock 진화, cosmic evolution 또는 Einstein feedback을 추가하지 않는다. 유한 energy support가 유한 radiation inventory를 뜻하지 않는다. physical secondary heat와 global error bound는 null이고, 원료 지원 밖 atomic event rate도 null이다. 이들은 0으로 채우지 않는다. 기본 source의 thermal component=0은 선택 no-deposition 규칙이다.

## API와 장부

`source_pair.py`는 표준 라이브러리만 사용한다.

| API | 의미 |
|---|---|
| `load_selected_case(*, redshift=2.479, channel='HI')` | 로컬 고정 row를 ordinary `json.load`로 읽어 `SourceCard`를 반환한다. 다른 z/채널과 바이트가 바뀐 card는 거부한다. |
| `represented_residuals(card)` | 정확히 표현된 입력의 r_B, r_E, gross_B, gross_E를 `Fraction`으로 반환한다. |
| `source_per_href(card, x_hi, amplitude=1)` | x_hi와 amplitude를 각각 한 번 적용한 proper-time per-Href source를 반환한다. |
| `source_jvp_fixed_moments(card, x_hi, dx_hi, amplitude=1, d_amplitude=0)` | 모멘트를 고정하고 dm = amplitude·dx_hi + x_hi·d_amplitude인 analytic JVP를 반환한다. |

x_hi와 amplitude는 유한·비음수이고, 방향 dx_hi와 d_amplitude는 유한 부호값을 허용한다. 상태 경계에서 방향은 물리 domain 안에서 해석한다. z, chi, support, angular derivative는 제공하지 않는다.

에너지 순서는 `(gas_thermal, binding, uv_radiation, dynamic_escape_radiation, source_reservoir, primary_nonthermal)`이다. source는 m = x_hi·amplitude에 대해 `m*(0,B,-P,0,0,K)`이고 JVP는 같은 계수에 정확한 dm을 곱한다. K는 저장된 직접 kinetic moment를 사용한다. K를 P−chi·A 또는 P−B로 복원하는 경로, B/P를 덮어쓰는 closure snapping, 잔차를 다른 소유자에 숨기는 correction은 없다.

입자 순서는 `(HI,HII,e_nt,e_th,absorbed_photon)`이며 `m*(-A,A,A,0,-A)`다. `PairRates.e_all_rate`는 e_nt+e_th의 파생 표현이고 별도 입자 pool이 아니다. 따라서 전하에서 전자를 중복 계수하지 않는다. thermal electron 수나 heat capacity를 새 일차 전자로 갱신하지 않는다.

`PairRates`는 에너지/입자 tuple, 정확한 m 또는 dm인 `multiplier_exact`, `expected_energy_sum_exact`, represented residuals, 선언된 closure 이름을 반환한다. `isotropic_flux0`와 `isotropic_stf0`는 명시적인 isotropic scalar closure의 0이다. 측정된 angular source, pressure trace, recoil/four-force 또는 transport calibration이 아니다. physical secondary heat는 별도 None으로 남는다.

## 표현과 잔차

ordinary JSON 파싱의 유한 float는 저장된 binary64 표현이다. 표시된 십진 spellings를 원래의 정확한 물리 입력으로 재해석하지 않는다. 내부 곱과 합은 int/Fraction/finite float의 정확한 Fraction 표현으로 계산한다. source의 m과 JVP의 전체 dm을 먼저 float로 반올림하지 않고 각 최종 float-containing active rate에서 한 번만 float로 변환한다. 최종 binary64 표현 범위를 넘으면 명시적으로 실패한다. 범위 내 최종 반올림은 upstream 입력 정밀도를 복원하지 않는다.

정확한 represented-input diagnostics는 다음과 같다.

- r_B = B − chi·A; gross_B = |B| + |chi·A|.
- r_E = B + K − P; gross_E = |B| + |K| + |P|.
- source의 정확한 기대 합은 m·r_E이고, JVP의 정확한 기대 합은 dm·r_E다.

최종 각 성분을 binary64로 반환한 tuple의 합에는 별도의 성분 반올림 오차가 있을 수 있다. 이를 입력 summary residual과 구분한다. 모든 source 합이 machine zero여야 한다고 요구하지 않는다. 공급자 `energy_ledger_residual_eV_per_target_s = -1.6155871338926322e-27`은 원래 필드와 부호 그대로 보존하고 우리의 r_E로 재명명하지 않는다.

**이번 준비에서는 수치 잔차, source 값, JVP 값 또는 수치 PASS를 계산하거나 보고하지 않았다.** 이 README의 공급자 수치는 이미 저장된 원료 필드의 인용이다.

## 향후 focused check와 실행 경계

`focused_check.py`는 작성만 했으며 import/compile/실행하지 않았다. 향후 별도 허용된 한 child 안에서 저장 row, 독립 exact-Fraction source/JVP reference와 최종 반올림, 직접 K/null 보존, 입자 핵수/전하, mixed cancellation 방향, unsupported z 한 건 거부를 검사하도록 준비했다. mixed 방향의 m/모멘트 정규화는 기존 source와 동일하며 중간 dm 반올림을 허용하지 않는다. 출력하는 input residual과 component-rounding residual은 서로 다른 항목이다.

이 fixture는 bounded runner가 아니다. 제안된 새 CPU 1 s / wall 5 s / retry 0 배정은 아직 승인되지 않았으며 L0 SRC-01의 배정을 전용하지 않는다. 미래 ledger criterion 2e-12는 이번에 고정하거나 시험하지 않았다. fixture는 최종 성분이 exact reference의 한 번 반올림과 같은지 확인하도록 준비했을 뿐 tolerance 기반 source qualification은 발행하지 않는다. donor quadrature나 기존 L0 campaign을 재생하지 않는다.

현재 L1 scientific invocations는 0이고 CPU는 `NOT_MEASURED_NO_L1_SCIENCE_EXECUTION`이다. executor 요청은 gpt-6.1-sol/high, 독립 관측 backend는 unknown이다. 다음 단계는 root/source reviewer의 읽기 전용 정적 검토다.
