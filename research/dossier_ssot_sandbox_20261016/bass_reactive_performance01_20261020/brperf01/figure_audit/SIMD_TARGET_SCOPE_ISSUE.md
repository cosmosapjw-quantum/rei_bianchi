# Recorded issue: host AVX capability versus compiled target configuration

**Priority:** P1 scientific-report wording. **Disposition:** recorded correction
for final publication; original frozen `rates/REPORT_RATES_KO.md` is unchanged.

The rate report's opening summary describes an “SSE2/no-AVX execution
environment.” That wording is too broad. The archived
`runtime_evidence/RUNTIME_IDENTITY.json` contains advertised host flags including
`avx`, `avx2`, `avx512f`, `avx512dq`, `avx512bw` and `avx512vl`. The rate evidence
`rates/evidence/LEGACY_BASELINE.json` instead records the particular build's
compile-time target-feature checks as `compiled_sse2=true` and
`compiled_avx=false`.

These two facts are compatible: the host advertises AVX/AVX512 support while the
crate was built for a more conservative target configuration. The later report
sentence specifically describing “this build” is appropriately scoped. The
next-DAG phrase “AVX-capable target” should distinguish an AVX-enabled target
build from acquiring an AVX-capable host.

Suggested publication wording:

> 호스트는 AVX/AVX2/AVX512 기능을 표시하지만, 이번 계수 수신기 빌드의
> compile-time target 설정은 SSE2=true, AVX=false다. 현재 측정에서 scalar
> 대비 추가 SIMD 가속은 확립되지 않았다. AVX를 명시적으로 활성화한 별도
> 빌드는 같은 정확도·입력·통계 조건에서 후속 검증해야 한다.

The feature checks are not disassembly evidence proving that every instruction
in the entire executable avoids AVX. No target flags were changed, no new
benchmark was run, and the optional SIMD path's existing parity result remains
distinct from its unestablished incremental speed advantage. The figure uses
only the latter measured statement and makes no claim of host incapability.
