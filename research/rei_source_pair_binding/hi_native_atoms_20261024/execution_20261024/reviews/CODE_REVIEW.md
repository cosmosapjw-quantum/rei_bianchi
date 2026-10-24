# Native HI C9 정적 검토 — 같은 독립 검토 pass

**판정: PASS_SCOPED_STATIC, finding 0, 수리 요구 0.**

검토자 `/root/source_intake`는 본 이론·구현·fixture·runner의 작성자가 아니다. 앞선 `THEORY_REVIEW.md`에 이어 실제 `native_source.py`, `focused_check.py`, `run_focused_once.py`, `PROPOSED_EXECUTION.json`, `SOURCE_BINDING.json`, README와 복사 입력 identity를 읽었다. import·test·science 실행은 하지 않았다.

## 실제 identity

Proposal SHA256은 `9cccccb0f2f12f531168de03a0aa8b7f3023f29320b13ff9c9246b0c767743ee`다. Proposal이 지시한 9개 파일의 실제 SHA256을 모두 확인했고 9/9 일치했다. CSV는 1,681,578bytes/SHA f5bcfe…이며 historical source card는 2,702bytes/SHA1b4077…다. API 원본을 바꾸거나 원 donor 실행을 호출하는 코드 경로가 없다.

## 식–코드 대응

- `load_selected_atoms`는 고정 CSV bytes/hash, HI/z2.479 selector와 행 수4,368을 확인한다. ASCII CSV decimal → binary64 → Fraction 순서가 정해져 있고 원 순서와 CRLF 파일 bytes를 보존한다. `_atoms`는 k≥0, w>0, χ+k≤50000과 nonempty 조건을 확인한다.
- `native_moments`는 exact A/K/B/P를 계산한다. P는 별도 Σw(k+χ) 계산이므로 fixture의 P=B+K 비교가 source code의 단순 복제만은 아니다. Integer-dyadic reference는 공통 2의 거듭제곱 denominator로 정렬하며 Fraction 합산 함수를 호출하지 않는다.
- `source_per_href_native`와 `source_jvp_native`는 normalization 및 dm의 곱·합을 Fraction으로 유지한 뒤 각 최종 component에서만 float 변환한다. energy/particle 순서, 핵수·전하 residual, primary nonthermal owner와 null이 계약과 일치한다.
- `_rounded_component`는 final overflow/nonfinite를 거절하고, finite adjacent spacing을 exact Fraction으로 사용한다. 최대 유한값에서는 유한 이웃 spacing을 사용한다. zero·최종 underflow-to-zero·subnormal·normal 태그가 구별된다. `_vector`는 exact/rounded components, component errors와 예산을 모두 남긴다.
- `rounding_decomposition`의 actual scalar operations는 provider의 k*w, k+χ, w*RN(k+χ), χ*a_hat 순서와 맞는다. A/K/P fsum 단계의 유한 1-ulp 비교, 저장 scalar 재현, exact delta 항등식 및 donor의 별도 P−B−K 잔차를 반환한다. 기존 2e−12나 donor quadrature tolerance를 고치지 않는다.
- Bin은 원 `bisect_right((10.0,9937.21),k)`를 유지한다. Bin별 exact sums·행 수와 저장 scalar를 함께 기록하고, 경계가 상위 bin으로 들어가는 별도 hand selector를 fixture가 포함한다.

## 검증 설계와 실행 전이

실제4,368행, independent dyadic moments, 네 delta identities, 손유도 두 atom, normalization1회, signed JVP, zero/tiny/subnormal, exact tiny×large normalization, 입력 거절이 한 fixture에 모여 있다. 공급자 quadrature/이전 HI·stock·work/ANGTHERM 시험을 호출하지 않는다. 원자 source를 pressure나 시간 evolution으로 확장하는 구현도 없다.

Runner는 root의 proposal-SHA GO와 9개 준비 파일 identity를 확인한 뒤 한 child만 시작한다. CPU soft/hard2s, wall10s와 retry0이 코드·proposal에 일치한다. 성공/실패 stdout·stderr·resource receipt를 모두 보존하며 runner 자체는 과학적 admission을 내리지 않는다. 과거 cap FAIL와 known partial·UNKNOWN_NOT_ZERO·NOT_FROZEN을 기록한다.

이 판정 뒤의 다음 실행은 root가 정확한 proposal을 GO에 결속한 **한 child**다. C6–C8의 실제 PASS와 C9 actual-raw 부분은 그 raw가 생긴 뒤 같은 검토 pass에서 확인한다. 본 정적 판정으로 아직 실행하지 않은 finite-data certificate나 CPU/wall 결과를 PASS 처리하지 않는다.
