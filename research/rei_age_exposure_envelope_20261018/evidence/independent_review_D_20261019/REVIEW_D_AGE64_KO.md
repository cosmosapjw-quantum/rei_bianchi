# D 구현 및 기존 age64 원자료: 독립 검토 복구본

**보고서 재구성 표시:** scratch 초기화 전의 도구 출력과 검토 기록에서 복구했다. 원래 검토 manifest의 기록상 SHA256은 `3f0644cc21a96d1f6f6f3c581095ad8f2623151afaebbd1ae2573ef838e129f3`이나, 원래 timestamp와 파일 바이트를 모두 확보하지 못했으므로 이 복구본이 그 SHA와 같다고 주장하지 않는다. 아래 실행·검토 결과는 초기화 전에 실제로 관측한 결과이며 캠페인이나 테스트를 다시 실행한 결과가 아니다.

검토자 `/root/runtime_probe`의 결과는 **`pass_scoped`**, 추가 blocking finding 0개다. 기존 A/B/C 검토와 별도로 수행한 검토이며 **`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`**를 유지했다.

## 1. D 구현의 범위

실제 `src/subnormal_count_rounding.py`, `src/prepare_native.py`, `tests/test_subnormal_count_rounding.py`, captured fixture와 `scripts/run_accuracy_followup.sh`를 읽었다.

- 원래 count gate가 실패한 branch에서만 보정을 시도한다. 양수 subnormal 입력, 유한한 비음수 subnormal 또는 0 중량, 기존 \(|F|<8\epsilon\) 수렴을 요구한다.
- `u128` checked 연산으로 정수 \(\eta=2^{-1074}\) 단위 합과 count 차이를 계산한다.
- `ticks > largest`일 때만 index를 바꾸므로 동률은 최초 최대 중량을 선택한다.
- 수정된 중량도 양수 subnormal이어야 한다. 0으로 만드는 후보도 거부하므로 수학적 비음수 후보보다 보수적이다.
- 원본 result를 clone한 후보를 만들고, 같은 compensated `sum()`으로 원래 \(64\epsilon N\) count gate와 \(128\epsilon S_U\) energy gate를 다시 검사한다. 실패한 후보는 원본 result를 바꾸지 않으며 원래 오류로 돌아간다.
- 기존 노드 위치·개수·순서를 유지한다. 하나의 중량만 \(d\eta\) 바꾸므로 \(L^1=|d|\eta\)이며 정확한 count를 회복하는 모든 보정 중 최소다.
- 고정된 유한 kernel에서만 \(|\Delta R|\le\max_i|K_i|\,|d|\eta\)를 주장한다. nonlinear solver의 전역 정확도 경계는 아니다.
- 성공 로그는 `FIRST_SUCCESS_ONLY; total applications not recorded`다. 전체 보정 횟수나 누적 경계를 기록했다고 주장하지 않는다.

### 준비·빌드·후속 실행

기존 stage1 prepare와 diff를 읽었다. 기본 `moment_rounding='none'`은 기존 원본/진단 prefix를 그대로 사용하는 branch이며 rounding key를 prepared identity에 추가하지 않는다. 재사용 시 mode, injection SHA, 준비 출력 hash를 대조한다. 실행 fingerprint에는 준비 identity와 binary SHA가 포함된다.

실제 D prepared transport에서 D·C 삽입문과 accessor suffix를 제거하면 frozen 원본 바이트가 정확히 복원됐다. 준비 identity, 빌드 receipt와 실제 binary SHA가 일치했고, 빌드 exit 0 및 빌드 중 준비 소스 변경 0개를 확인했다. 이는 초기화 전에 수행한 검증이며 현재 잃어버린 binary를 다시 검증했다는 뜻은 아니다.

검토자는 실제 삽입 바이트를 컴파일하는 captured fixture와 fail-closed 대조군 테스트 하나를 직접 실행했다. exit 0, 1 test PASS였다. 원래 결과는 `D_COMPILED_FIXTURE_REVIEW_TEST.json`에 복구했다. 구현 담당자의 전체 crate 빌드와 로컬 smoke는 실제 receipt와 파일을 읽어 확인했으며 검토자가 전체 solver를 재실행하지 않았다.

후속 script는 `age64-block-max`와 `time8-subnormal-count`를 명시적으로 하나씩 선택한다. 전자는 일반 native 준비본에서 block-max reference를 선택하고, 후자는 D+C opt-in을 선택한다. 기존 전체 캠페인을 자동 실행하지 않는다. 현재 time8 실패를 이미 확인했으므로 이 script의 존재를 같은 실행을 반복할 READY 근거로 해석하지 않는다.

## 2. 실제 D time8: 첫 보정 성공, 이후 energy-only 실패

실제 stderr의 최초 성공·후속 실패를 JSON과 대조했고 출력 노드로 count 및 energy 계산을 독립 재구성했다.

| 항목 | 초기화 전에 실제 확인한 결과 |
|---|---:|
| 최초 보정 \(L^1\) | \(5\eta\) |
| 최초 count defect | \(5\eta\to0\), 허용치 \(3\eta\) |
| 최초 energy defect | \(89\eta\to4\eta\), 허용치 \(116\eta\) |
| 후속 실패 셀 \(N\) | `6.149329425376e-312` |
| 후속 count 합 / target | `1244638132025` / `1244638132025` quantum |
| 후속 count defect / tolerance | 0 / 0 |
| 후속 energy defect / tolerance | \(2\eta/\eta\) |
| 전체 실행 | 6.849초, timeout 없음, exit 1, `FAILED` |

후속 셀은 count가 이미 정확하므로 D 적용 조건이 거짓이다. 원래 `MOMENT_FIT`를 유지하는 동작이 계약에 맞다. 최초 count 실패를 보정한 사실과 time8 전체 완료·수렴성은 구분해야 한다. 전체 보정 횟수도 확보하지 않았다.

후속 셀의 128개 노드 배열과 원래 stderr 전체 바이트는 표시된 도구 출력에 남아 있지 않아 초기화 후 복구하지 못했다. 보존된 측정 수치와 기존 독립 검증 결과를 compact 복구본으로 구분한다. 잃어버린 배열을 새 실행으로 대체하지 않았다.

## 3. 기존 age64의 독립 정확 합산

초기화 전에 원자료 70개 모두 SHA256, Git blob SHA와 size를 확인했고 불일치는 0개였다. ZIP 바이트 identity까지 확인했다는 주장은 하지 않았다.

별도 analyzer를 호출하지 않고 endpoint의 광자 수와 photoevent 3항, setup의 source birth 64항을 읽어 **68개 저장 binary64 항**을 `Fraction`으로 정확히 더했다.

\[
\mathcal R=\frac{14226514013909}{9671406556917033397649408}
=1.4709870720649348873682\ldots\times10^{-12},
\]

\[
\mathcal G=\frac{1411110823296896384725}{9671406556917033397649408}
=1.4590543939936674335139\ldots\times10^{-4},
\]

\[
|\mathcal R|/\mathcal G=1.0081783640969037401690\ldots\times10^{-8}>10^{-8}.
\]

정확한 residual 및 gross는 analyzer의 exact fraction과 일치했다. 기존 저장 assertion, `math.fsum`, 정확한 유리수 합 모두 gate를 실패했다. 기존 binary64 `TARGET=1e-8`에 대한 residual 한계 초과분은 `1.1932678071267423e-14`다.

저장 residual과 정확한 residual의 차이는 `1.6486226596064687e-20`이며 마지막 68항 합셈의 \(\gamma_{68}\mathcal G\) 경계는 약 `1.1015155320267548e-18`다. 초과분이 이 경계보다 약 **10,832.96배** 크므로 최종 합셈만 정확하게 바꾸어 기존 endpoint를 통과시킬 수 없다.

이 결론은 최종 저장항 합에 한정된다. RHS, adaptive time step, source insertion의 기여를 이 계산으로 분해하지 않았다. Interval 65개를 이 검토에서 재계산하지 않았고 paired source-jump는 missing이다. `history_interpretation=UNRESOLVED`를 유지한다.

## 복구 파일과 미해결 범위

네 subordinate JSON은 당시 전체 표시된 도구 출력에서 수치를 복구했다. 최종 manifest와 본 문서는 report reconstruction으로 표시했다. 원래 바이트를 대조하지 못한 복구 파일에는 새 SHA를 따로 기록한다.

D 최초 count 보정은 관측됐으나 native time8은 후속 energy-only 오류로 실패한다. Age64 endpoint는 정확한 최종 합에서도 gate를 실패한다. 새로운 block-max age64 결과, native-time 교정·수렴성, age/source/spectral 정확도는 미해결이다. 코드 범위를 확대하거나 같은 캠페인을 반복할 근거를 이 검토에서 추가하지 않았다.
