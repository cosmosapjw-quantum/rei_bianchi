# COLD_CONDITIONAL_FLRW_IVP01 관측 결과

기계 실행 검증 PASS. 독립 Astra 판정은 `PASS_SCOPED_AFTER_EVIDENCE_REPAIR`이며 scientific blocker는 발견되지 않았다. 승인 범위는 “four source-pinned, finite cold FLRW conditional intervals over tau in [0,1e14] s, with independent Decimal80 reference agreement and observed RK4 refinement.” Bianchi background/IC adoption, CR, helium reactions, radiation backreaction, global admission, physical-continuum certification은 HOLD이다.

Published base `55091ff938f3a4649bef808f1ec83ac5d29384fb`, tree `5b5d5bfd9b0119d934bb6972a90676adbc5eaa2c`에서 격리 worktree/branch를 만들었다. 원본 dirty checkout을 보존했다. 빌드 전에 source-only local commit `c5e824fd2ec5cd41f62ea0aaade2c1edbfa6c772`, tree `1971165e9485fd9eff15cbca9cd4282fa9bb665f`를 고정했다. 이 commit은 실행 입력을 고정하기 위한 local provenance이며 push하지 않았다. HARNESS_UNAVAILABLE: `/home/cosmosapjw/.codex/bounded-work-harness/RULES.md`가 없다.

실제 production stage callback은 매 RK4 stage의 13종 isotope density와 thermal energy에서 EOS, xe, RR 및 Compton을 평가했다. `a`와 네 개의 별도 ledger를 동시에 적분했다. time tag guard만 finite nonnegative로 확장했다. 독립 Decimal80 oracle은 reduced `(a,xe,T)` 방정식 및 ledger를 계산하며 production callback을 호출하지 않는다. Clipping, fallback, H rescale은 없다.

깨끗한 별도 target 디렉토리에서 release build 1회, 1.818 s. Binary SHA256 `300e3f3a52f37f8388b1450d609f3db5cba3a0c4c8698244553158843821fae2`. 의도적으로 잘못된 binary hash를 넣은 preflight는 solver 시작 전에 거부했다. 실제 source/binary preflight는 PASS. Native campaign 1회, 0.0157 s. Native 14 trajectories / 288 steps / 1168 derivative attempts. Reference 4 trajectories / 512 steps / 2048 RHS attempts. 추가 solver/reference 실행은 없었으며 evidence-report repair 1회가 있었다.

15,489 numerical PASS checks + 4 refinement-status records = 15,493 entries (Astra-authorized evidence repair 이후). 최대 N32/Decimal80 norm `1.3818541424493926e-13`; 최대 N16/N32 norm `2.0788900200965023e-12`; 최대 N8/N16 norm `3.3357450087908035e-11`. 네 endpoint 모두 frozen refinement rule을 통과했다. Norm field scales는 VALIDATION.json에 저장했다. 독립 reference의 nonzero final ledger magnitude는 trajectory comparison norm에만 사용한다. 초기값 또는 conservation residual scale로 사용하지 않는다.

각 epoch의 chemistry denominator는 `|chem0|+|a^3 nHII|+|Rc|`, HI는 `|HI0|+|a^3 nHI|+|Rc|`, He는 `|He0|+|a^3 nHe|`이다. Energy denominator는 `|energy0|+|a^3(u+chi*nHII)|+|Eesc|+|Ebath|+|W|`이다. 수정 후 최대 chemistry residual `4.610436505744918e-16`, HI `2.9250400426377583e-16`, He `5.819109203636471e-16`, energy `4.708702802691698e-16`, baryon `3.3700364394062887e-16`, helium `5.819109203636471e-16`. Chemistry/HI/He/energy threshold `1e-10`와 기존 baryon/helium `1e-11`은 유지했다. Stage oracle 최대 `1.5717391978200234e-15`, source oracle `1.452871056219239e-15`, stage energy `6.932089821962916e-17`, stage hydrogen source exactly zero. Source-free analytic invariant 최대 `4.498365609479314e-15`; xe0 expansion-only 최대 `4.499218135302421e-15`. Unsupported species 및 source-free/xe0 reaction ledgers는 exact zero. t0/positive derivative equality, negative/NaN rejection은 native driver에서 확인했다.

아래는 각 epoch의 native/reference ledger relative error다. Denominator는 해당 epoch의 `max(|native|,|reference|)`이며, 둘 다 zero이면 exact equality를 요구하고 error를 zero로 기록한다. 이 denominator도 comparison-only이며 초기값 또는 residual scale이 아니다. Epoch 0은 모든 endpoint/ledger에서 exact zero다. Full precision 값과 denominator는 VALIDATION.json의 `ledger_relative_errors`에 있다.

|Endpoint|Epoch fraction|Rc|Eesc|Ebath|W|
|---|---|---|---|---|---|
|0|.25|5.176392e-14|5.157027e-14|1.191202e-14|1.434668e-13|
|0|.50|5.109723e-14|5.085283e-14|1.170542e-14|1.416600e-13|
|0|.75|5.069829e-14|5.034731e-14|1.144649e-14|1.396197e-13|
|0|1.00|5.002276e-14|4.983792e-14|1.113422e-14|1.381854e-13|
|1|.25|1.351444e-14|1.345004e-14|2.097969e-15|3.915812e-14|
|1|.50|1.333053e-14|1.364607e-14|2.108516e-15|3.885444e-14|
|1|.75|1.314574e-14|1.339260e-14|2.260350e-15|3.854770e-14|
|1|1.00|1.317253e-14|1.319435e-14|2.129654e-15|3.812675e-14|
|2|.25|5.149292e-14|5.135451e-14|1.162498e-14|1.432592e-13|
|2|.50|5.096135e-14|5.063645e-14|1.141640e-14|1.414514e-13|
|2|.75|4.997145e-14|5.005797e-14|1.105848e-14|1.397595e-13|
|2|1.00|4.947608e-14|4.940267e-14|1.098772e-14|1.381854e-13|
|3|.25|1.393678e-14|1.361819e-14|2.307767e-15|3.915813e-14|
|3|.50|1.354214e-14|1.347762e-14|2.319369e-15|3.863368e-14|
|3|.75|1.300441e-14|1.328007e-14|2.260351e-15|3.854770e-14|
|3|1.00|1.296008e-14|1.302520e-14|2.342621e-15|3.846022e-14|

Astra가 승인한 minimal evidence/validation/report repair는 stored native trajectory 및 stored Decimal80 reference만 읽었다. Build, native solver, reference integrator를 재실행하지 않았다. `FIRST_*`, build/campaign/prelaunch receipts 및 reference의 SHA는 repair 전후 동일함을 `VALIDATION_REPAIR_RECEIPT.json`에 기록했다. Original validation은 `VALIDATION_BEFORE_REPAIR.json`에 보존했다. 물리 모델, solver 및 tolerance 변경은 없다.

원시 native stdout/stderr, 입력, clean-build receipt, prelaunch receipt, stale-binary negative receipt, independent reference와 전체 검증은 `evidence/`에 보존했다. 독립 review에서 보존 artifact 9개의 hash 및 build-manifest source hash가 일치했다. 최대 ledger relative error는 `1.434667701520813e-13`이다. `git diff --check` PASS. Scoped publication 이후 다음 후보는 Astra planning으로 결정한다.
