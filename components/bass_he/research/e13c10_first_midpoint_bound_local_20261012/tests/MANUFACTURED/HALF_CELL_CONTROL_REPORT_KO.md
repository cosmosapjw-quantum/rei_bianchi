# E13C10 left-half Peano refinement 추가 대조

## 결과와 실행 범위

동일 N의 unrefined raw endpoint 실패를 보존한 뒤 추가한 left-half Peano refinement를 **첫 실행에서 통과**했다. 실제 exit code는 0이다. 새 `EXEC03_HALF_CELL`만 실행했고, 이전 EXEC01·EXEC02 또는 unrefined integrator를 재실행하지 않았다.

고정 후보의 식은 각 원래 cell에서 `h/(48*N³) * (D_left_half + D_whole_parent)`이다. Peano kernel의 양의 적분 질량은 각 반셀에서 `1/(48*N³)`이고, whole-parent derivative enclosure는 우반셀에서도 유효하다. 이 대조는 그 계수·부호·분기와 실제 캐시 동작을 확인한다. 이전 구간과 교차시키거나 작은 실패를 무시하는 허용 오차를 추가하지 않았다.

| 항목 | 실제 값 |
|---|---:|
| 제조 문제 | 6 |
| branch별 실행 | fresh-parent 6, cached-parent 6 |
| N / 후보 precision / oracle precision | 8 / P60 / P140 |
| 검사 통과 / 실패 | 993 / 0 |
| 신규 whole-cell 계수 평가 | 48 |
| 신규 left-half 계수 평가 | 96 |
| 신규 midpoint 평가 | 0 |
| 전체 제조 계수 평가 | 144 |
| 별도 parent-cache setup 평가 | 0 |
| unrefined integrator / 기존 suite 재실행 | 0 / 0 |
| captured 계수 / ODE / NCP | 모두 0 |
| suite wall / CPU | 0.476905332 s / 0.476907144 s |
| 명령 전체 wall | 0.528225851 s |
| 해당 프로세스 peak RSS | 53,408 KiB |
| 실제 exit / 첫 실패 / 재시도 | 0 / 0 / 0 |

## Cache의 실제 의존성과 검증

Midpoint aggregate는 pin이 확인된 기존 EXEC01의 동일 case·N8 결과에서 읽었다. Parent curvature는 각 case의 **이번 fresh-parent refined 실행**에서 이미 얻은 whole-cell derivative 필드를 사용했다. 이 필드를 별도 `*_PARENT_CURVATURE.json`으로 저장한 뒤, 같은 case·N/P/source의 cached-parent branch에 전달했다. 따라서 별도 setup을 숨기거나 parent derivative를 만들어낸 것이 아니다.

Fresh-parent branch는 whole-cell N회와 left-half N회, cached-parent branch는 left-half N회만 호출했다. 제조 계수 객체는 입력 cell의 정확한 Fraction 폭으로 두 호출 종류를 구분하고 point 호출도 별도로 셌다. 후보가 보고한 count와 실제 count가 일치했다. Midpoint와 parent-cache 입력은 변경되지 않았고, 양 branch의 signed output과 curvature correction은 endpoints가 정확히 일치했다.

이는 분기 및 cache 보존의 동작 확인이다. 수치 포함의 독립 기준은 별도로 계산한 integrated-response 닫힌식이며, 두 branch의 일치 자체를 독립 oracle이라고 부르지 않는다.

## 필요한 제조 문제

Exact zero, 양·음 quadratic forcing, centered cubic의 곡률 부호 전환, L>0에서 종별 defect의 total cancellation, L=0에서 nonzero opacity defect를 선택했다. 각 branch의 17개 signed output이 P140 독립 닫힌식 값을 포함했고, 수·에너지·종별 heat ledger가 0을 포함했다. Analytic incoming gain을 더한 결과도 nonzero center/radius의 `-eta`, `0`, `+eta` 값을 포함했다.

Quadratic ±에서는 정확한 `±1/24`를 양 branch 모두 폭 `1e-61`의 구간으로 포함했다. 이 검사는 반셀 질량의 2배 오류와 잘못된 곡률 부호를 구분한다. Centered cubic의 정확한 적분 0은 두 branch 모두 대략 `[-1.52587890625e-5, 7.62939453125e-6]` 구간에 포함됐다. 좌반셀만 좁힌 비대칭 enclosure를 그대로 보존하며, 대칭화나 구간 교차는 하지 않았다.

## 코드 이력과 증거

이번 수정 후보 SHA는 실행 전후 모두 `574e797e563820fb669a9b8e5d10cad21e598d9a64f9a3f4b79af1737c48acfa`이고, 실행 계약 SHA는 `467333ed1123008aa2e43c81016269ad14e69bf4aef0f58804dbc1dc1a761459`이다. 이전 code/contract는 INITIAL_N32 및 SAME_N_UNREFINED 보존본을 각 이전 receipt의 실제 pin과 대조했다. 과거 성공 receipt를 이번 코드의 과거 실행으로 표시하지 않는다.

| 파일 | bytes | SHA-256 |
|---|---:|---|
| `run_half_cell_controls.py` | 17,869 | `2ecba241eff944219ab25e17b5d1f059de8a2bc46fa744e6145a569e35af59f2` |
| `EXEC03_HALF_CELL/CONTROL_RESULTS.json` | 885,840 | `0a8fcfbde1d5c5cc1bdc49511847524032364ce239d626d6990b6e277437180c` |
| `EXEC03_HALF_CELL/RECEIPT.json` | 2,548 | `e0c2af57c881e078189cdceae438d1e7a1adab23a1367080bb1a02da36a43dcf` |
| `EXEC03_HALF_CELL/COMMAND_RECEIPT.json` | 1,152 | `cfdab68e8150c9351bfb2b567648ec22f9e144ab34b84921aa2aaf0e2e8c1772` |

START, raw results, 각 case의 parent cache, receipt, 실제 argv·UTC·exit 및 stdout/stderr를 새 EXEC03_HALF_CELL 폴더에 보존했다. 독립 공식과 evaluator는 이전 control source에서 pin을 확인한 함수를 가져왔으며, 기존 suite의 main은 실행하지 않았다. Decimal exp primitive의 공유와 제조 모델이라는 한계는 그대로다. 작성자는 control 기여자이고 최종 독립 reviewer가 아니다. 이 결과가 captured raw admission 실패를 지우거나 최종 selected/full/physical 판단을 대신하지 않는다.
