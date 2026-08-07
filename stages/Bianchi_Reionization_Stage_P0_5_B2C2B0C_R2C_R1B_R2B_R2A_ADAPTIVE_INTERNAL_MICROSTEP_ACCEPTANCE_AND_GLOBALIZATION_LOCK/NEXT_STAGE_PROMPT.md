# Next exact stage prompt

@Web+Wolfram Stage `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT`를 실행해줘.

R2B-R2A의 state, owner law, array-native kernels, safeguarded globalization,
transaction semantics, 17-node forcing와 ten-ledger 구조를 정본으로 유지한다.
현재 `dt/1024`에서 fixed-point와 모든 conservation gate는 닫히지만 hard
maximum local error `8.3986559e-4`가 `2e-4`를 초과하며, post-lock auditor는
`dt/4096`에서 `7.8722763e-5`로 통과한다.

1. 계산 전에 새 durable directory, input lock, stage state, receipts,
   manifest와 SHA256SUMS를 생성한다.
2. 결과를 보기 전에 다음 후보를 잠근다.
   - primary: second-order nonautonomous modified Patankar Runge–Kutta
     thermochemistry for the H/He production–destruction block;
   - thermal coupling: independently implicit positive thermal solve at every
     MPRK stage with a declared embedded/step-doubling estimator;
   - auditor: existing backward-Euler operator at partitions 1024, 2048, 4096.
3. MPRK candidate는 H/He nuclei를 대수적으로 보존하고 모든 species를
   clipping 없이 양수로 유지해야 한다. Unsupported owner/group와 subgrid
   resolved source는 exact zero다.
4. Nonautonomous forcing은 stage time에서 canonical BDF interpolation으로
   평가한다. `kappa=J/Phi`, per-node fitting, owner 이동은 금지한다.
5. 먼저 첫 segment에서 BE와 second-order candidate를 partitions
   512,1024,2048에 비교한다. Hard maximum coordinates는
   `x_HII,x_HeII,x_HeIII,logT`를 유지한다.
6. Candidate가 partition 1024 또는 2048에서 local-error `2e-4`를 닫고
   positivity/conservation/thermal/photon gate를 모두 통과해야 adaptive
   first-interval production 후보로 승인한다.
7. Candidate가 실패하면 partition 4096 BE 결과를 production으로 승격하지
   말고 deterministic cost/feasibility auditor로만 유지하며 bounded no-go를
   남긴다.
8. 성능 gate는 동일 정확도에서 BE-4096 fallback 대비 wall time과 map-call
   수를 비교한다. JAX는 science-sequence stability가 재검증되기 전까지
   production backend로 사용하지 않는다.
9. Primary와 두 auditor lane을 모두 실행하고 post-hoc lane selection을
   금지한다.
10. `rec_bianchi`는 최신 SHA를 재확인하되 semantics-only monitoring을
    유지하고 numerical adapter/splice/surrogate는 시작하지 않는다.
11. unresolved subtraction, front/Q_M, source/fesc fitting, CAMB transfer,
    Bianchi feedback은 시작하지 않는다.

모든 gate가 닫힌 뒤에만 adaptive first canonical interval을 승인해줘.
