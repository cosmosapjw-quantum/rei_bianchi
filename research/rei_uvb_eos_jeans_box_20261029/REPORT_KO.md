# REI 2026-10-29 새 연구 단위 결과와 재현성 복구

## 최신 연구 재사용

PR248 17-state prescribed-bath pilot 7/7 재실행 없음, PR251 고정 Puchwein template / 7-point BB13 full covariance, PR252 single redshift tilt 18/20 재실행 없음, PR253 EOS-only tilt θ∈[-1,1] 18/20 (C8 그림 CPU overrun, R6/C9 대기), PR254 clean checkout repaired, PR255 exact-rational/Wolfram EOS-only 교차검증이 선행 근거다.

이번 연구는 EOS-only의 중복이 아니라 **7개 redshift-specific Jeans smoothing 구간을 추가하여 β, κ의 공동 affine support**를 구했다. primary source Becker & Bolton2013 Table1·2 외의 2026년에 새 추정한 자료가 아니다.

### 조건부 계산 실제 결과

| 값 | Source-bounded 값 |
| --- | --- |
| nominal κ₀ | 0.068661739480590678 dex/redshift |
| EOS+Jeans κ min | 0.053617504767915498 dex/redshift |
| EOS+Jeans κ max | 0.099225339666118351 dex/redshift |
| EOS+Jeans β min | -0.13087466565371772 dex |
| EOS+Jeans β max | 0.051206812137275709 dex |
| GLS covariance pivot | 7/7 exact positive |
| Exact vertices and nested model | 256 corners PASS |
| Independent NumPy reference | 4 extrema within 3e-17 |
| Wolfram independent engine | 4 extrema and projected derivative matched |
| Targeted unittest saved result | 8/8 PASS |

그림 `results/ZONOTOPE_SUPPORT.png`는 256 outer-box 꼭짓점의 2D convex hull, 기존 EOS-only 선분과 PR252 nominal 한 점을 분리해 표시한다. 실제 직접 이미지 readback PASS. 

### 별도 PR254 재현성 복구

[PR254 sibling clean CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40722462146)는 source Git blob 9/9, 원본 clean checkout `results/` 없음, post-fix 24/24 Python 테스트 PASS, 13 source/reference guards PASS. 0.20 wall, 0.08 user+0.01 system CPU, RSS14464KiB, exit0; GitHub source code와 관측 원본은 변경하지 않음. [원시 CI artifact](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40722462146/artifacts/12830273306)는 5400 bytes SHA256 `93a063aeb75db23cb96f0c6d72d1df1aae3bea7776c3d334d8c6250ba777b4d3`. Drive `1HwD2Kg4H8jWDgREXshkFs_cUigJeiJtn`, Dropbox `id:BSpOijBcT10AAAAAAEGpXA` 완료. 별도의 Rust repository-wide cargo fmt CI 실패는 해당 UVB Python 검증 성공과 혼동하지 않는다.

### 실제 새 실행과 자원

Exact Fraction worker user0.37+sys0.00 CPU-s, wall0.37s; NumPy reference user1.16+sys0.08 CPU-s, wall0.84s; 8-test suite user0.03+sys0.01 CPU-s wall0.04s; zonotope figure user1.44+sys0.12 CPU-s wall1.57s. Commands and raw stderr/stdout/time are preserved. 그림은 실제 제한 8 CPU-s로 실행했으나 최초 frozen allocation에는 포함되지 않았으므로 resource allocation은 `CONCERN_FIGURE_NOT_PREFROZEN`이다. Model, tool transport, remote publication and other unmetered tails `UNKNOWN_NOT_ZERO`; old exhausted reservations are not reset nor transferred. No global cumulative budget PASS claim.

### 수용 범위

`MATHEMATICALLY_DERIVED_AND_NUMERICALLY_CHECKED_CONDITIONAL_SUPPORT`, independent distinct-author R6/C9 `NOT_RUN`. Local work R1–5,R7–10 and C1–8,C10: 18/20; original canonical28/88, owner working33/88 unchanged. Physical F4 remains PARTIAL, L4 false, actual native25/temperatures/physical radii null. H–Li registry 26 ground+5 nuclear excited/102 formal requests are NOT new active species and do not change 17-state solver. No ODE/IVP or actual photonic source transfer.
