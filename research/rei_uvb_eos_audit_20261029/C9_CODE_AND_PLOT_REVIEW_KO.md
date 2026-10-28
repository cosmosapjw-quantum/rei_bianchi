# C9에 제공할 계산·시각증거: 독립 심사 미완료

이 작업은 PR252 R6/C9의 신규 실제 독립 모델 심사를 **대체하지 않는다.** 기존 PR252의 실수치·검증·배포 근거(18/20)는 재사용한다. 새로운 것은 *인쇄된 EOS nuisance 응답을 한 방향으로 이동한 결과*와 그 그림을 점검한 것이다.

## 실제 코드 실행

- `code/eos_linear_audit.py`: 원본 source field projection SHA256을 exact match 후 Fraction.from_float의 source binary64 실수상, 원 논문 인쇄 EOS v의 유리수상을 구성한다. 분해가 아닌 Fraction Gauss–Jordan, 고정 X=[1,z−3.6]의 rank2/정보 양정치, 정확한 Q 분해·nested improvement·공통 amplitude shift 등식, θ=−1,0,+1의 직접 residual-quad와 다항식 일치를 확인. Original PR252 scientific worker를 import하거나 rerun하지 않음.
- 원 실행 한 번, exit0. 실제 `/usr/bin/time`: user0.03 + system0.01 CPU-s, wall0.04s, 최대 RSS 12160 KiB, 주소 512MiB/CPU2s/wall12s 제한.
- 결과: `results/EOS_EXACT_RATIONAL.json`, `results/STDERR.txt`, `results/EXIT_CODE.txt`, `results/TIME.txt`. Wolfram 한 번의 외부 수치 계산은 별도 출처이며 모델 독립 리뷰가 아님.

## Plot CRAG 첫 검사 → 실제 표현 오류 → 한정 수정

- 첫 `plot_saved_eos.py` 계산은 θ∈[−1,1]에서 **x좌표를 1.2+0.2 θ**로 잘못 바꿨다. 이러면 표시된 γ축 범위가 1.0..1.4가 되고 θ=0의 실측 선택점을 γ=1.4에 올리면 곡선과 만나지 않는다. `figures/attempt_01_before_axis_repair/`에 첫 그림·코드를 원문 보존했다.
- 구체적 수정 1개: x좌표를 **γ=1.4+0.2 θ**로 교정하고 끝점 1.2, 중앙 1.4, 끝점 1.6을 assertion으로 추가했다. 물리 방정식, selected PR252 code/data나 수치 결과는 수정하지 않았다. 그 뒤 1회 표적 재렌더, exit0.
- 직접 최종 PNG 둘을 읽어 θ=0 선택점이 곡선 위, γ 양 끝점이 올바른 값, 단위/legend/주장 제한이 유지됨을 확인. 범주를 연속 기울기로 오인하는 선 연결 문제 없음. 시각 자료만으로 새로운 수치 수용을 선언하지 않는다.
- Presentation cost: first user3.78 + system.23 CPU-s, one repaired render user3.64 + system.20 CPU-s = **7.85 CPU-s** actual waited commands, unknown model/provider/publishing overhead separate. 이 합계는 과거 닫힌 presentation grants로 청구된 것이 아니며, cross-branch cumulative PASS를 주장하지 않는다.

## 보존 identity 및 종결 상태

Source SHA/미계측 비용은 manifest와 RUN_BUDGET 참고. 두 실제 signed-endpoint가 corrected figures에 일치한다. Original unit **18/20**, R6/C9 `PENDING_NATIVE_DISTINCT_AUTHOR`, physical-F4 partial, working DAG33/88, central28/88, delta0. 더 큰 원자/핵 IVP 및 source rerun은 금지한다.
