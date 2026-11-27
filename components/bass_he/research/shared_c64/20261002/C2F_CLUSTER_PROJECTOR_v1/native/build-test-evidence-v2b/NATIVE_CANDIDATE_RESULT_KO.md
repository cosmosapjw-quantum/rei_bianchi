# C2f native 최종 후보 결과

Fortran binary64/OpenMP/SIMD 구현과 정확도 검증은 완료했다. 최종 8-lane 보정 합산 후보는 17개 manufactured 검사를 통과했고, compiler report에서 실제 16-byte SIMD 생성도 확인했다. 다만 이 호스트의 동일 입력 public-API 측정에서는 모든 작업량에서 reference가 더 빨랐다. 이 범위에서는 reference를 명시적으로 선택하고 native는 정확도 검증된 선택지로 유지한다.

| OpenMP threads | N | rank | reference 중앙값 (ms) | native 중앙값 (ms) |
|---:|---:|---:|---:|---:|
| 1 | 4096 | 5 | 0.301 | 0.738 |
| 1 | 65536 | 5 | 3.638 | 7.430 |
| 1 | 131072 | 6 | 9.956 | 23.457 |
| 4 | 4096 | 5 | 0.291 | 0.632 |
| 4 | 65536 | 5 | 4.748 | 6.847 |
| 4 | 131072 | 6 | 11.634 | 17.563 |

각 행은 동일 실행 내 두 backend의 7개 교대 측정 중앙값이다. BLAS는 1 thread다. API 유한성·identity 검사와 필요한 column-major 복사 비용을 포함한다. 최대 절대 parity 차이는 $4.01\times10^{-17}$ 미만이었다. 이 수치는 정규화된 manufactured 입력 범위의 수치 비교이며 물리적 observable이나 연속체 gap의 오차 인증은 아니다.

실제 호스트의 CPU quota는 8 cores, memory limit는 8 GiB였으며 NCP 64코어 실측이 아니다. 서로 다른 benchmark 회차의 reference 시간도 변했으므로 최초 구현 대비 확정적 속도 향상률을 주장하지 않는다. 최종 후보의 로컬 native 승리도 주장하지 않는다.

최초 source/adapter/strict/debug binary는 `native/baseline_v1/MANIFEST.json`에 결속하여 보존했다. 첫 lane 후보가 정확도 검사는 통과했지만 vectorization에는 실패한 기록도 보존했다. 피연산자 선택을 먼저 수행하도록 수정한 최종 후보에서만 실제 SIMD를 확인했다.

근거는 `runs/BENCHMARK_V2B_OMP1.json`, `runs/BENCHMARK_V2B_OMP4.json`, `native/build-test-evidence-v2b/TEST_REPORT.json`, `native/build-v2b/vectorization.txt`다. 구현과 실패 모드의 자세한 설명은 같은 폴더의 `NATIVE_KERNEL_NOTES_KO.md`에 있다.

이 측정으로 최적화 루프를 종료한다. Production default 변경, implicit fallback, 물리 계산, D1/Eq55, NCP64 scaling 주장은 모두 없다.
