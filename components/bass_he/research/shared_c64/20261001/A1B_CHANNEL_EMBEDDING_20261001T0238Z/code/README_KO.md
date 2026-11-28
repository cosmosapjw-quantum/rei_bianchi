# A1b의 작은 행렬 검증

`channel_embedding_algebra.py`는 정규화된 target orbital 하나와 서로 직교하는 projectile orbital 다섯 개의 overlap vector `s = V†u`를 입력으로 받는다. `S`, `W`, 두 물리 projector의 quadratic form과 직교 partition을 계산한다. 일반 orbital, ETF, 시간 전파, collision amplitude, cross section을 계산하지 않는다.

- `gram_from_overlap(s)`: `S = [[1, s†], [s, I5]]`.
- `orthonormalizer(s)`: `Y = XW = [(u − Vs)/sqrt(delta), V]`, `delta = 1 − s†s`.
- `channel_probabilities(c, s)`: `c=(a,b)`에 대해 `p_B = ||b+sa||²`, `p_A_raw = |a+s†b|²`, `p_A_orthogonal = delta |a|²`, `metric_norm = c†Sc` 및 두 합을 반환한다. 입력 state를 자동 정규화하지 않는다. 정규화 전에는 모두 quadratic form이다.

유한 overlap에서 raw 물리 projector 두 개는 직교하지 않는다. 따라서 `p_A_raw + p_B`를 확률 partition으로 사용하면 안 된다. `p_A_orthogonal`은 `Ran(V)`의 직교 여공간 성분이며 raw target projector와 다르다.

고정 조건 `delta > 1e-12`를 만족하지 않는 입력, 잘못된 shape, 비유한 입력과 산술 overflow는 `ValueError`로 거부한다. 이 cutoff는 계산용 제한이며 physical completeness나 정확도 보증이 아니다. 정칙화·eigenvalue clipping·symmetrization·fitting은 하지 않는다.

실행 명령은 이 디렉터리에서 `python -B -m unittest -v test_channel_embedding_algebra.py`다. 검증은 복소수 8차원 ambient-space 구성, 물리 projector의 직접 적용, finite-overlap double counting 반례, zero-overlap 극한, 같은 중심 내부의 U(5) covariance, coherent cancellation, 제공된 analytic coalescence overlap, 입력 거부를 다룬다. 비교 허용오차는 절대 `2e-12`, 상대 `0`이다. coalescence overlap의 공간적 물리 유도 자체는 이 테스트의 증명 대상이 아니다.

`run_new_checks.py`는 test evidence를 한 번만 기록한다. 기존 evidence를 덮어쓰지 않는다. 재실행이 필요하면 이 code 디렉터리를 별도 경로로 복사하고 빈 sibling `evidence/newtest`를 사용한다. 기존 A1 또는 collision suite를 실행하지 않는다.
