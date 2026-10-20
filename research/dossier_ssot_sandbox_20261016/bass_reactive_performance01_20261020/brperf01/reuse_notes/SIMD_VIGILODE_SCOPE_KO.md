# BRPERF01 — SIMD 대상과 VigilODE 재사용 범위 교정

이 문서는 완성된 결과를 읽기 전용으로 검토한 추가 설명이다. 새 science run, test, benchmark 또는 solver activation을 하지 않았다. 기존 `rates/`, `atomic_theory/`, 물리 owner와 검증 산출물은 수정하지 않았다.

## 1. CPU 기능과 컴파일 대상을 구분

권장 최종 표현은 다음과 같다.

> 이번 측정은 AVX·AVX2·AVX-512 기능이 노출된 CPU에서 수행했지만, 바이너리는 AVX를 활성화하지 않은 기본 x86_64/SSE2 대상으로 컴파일했다. scalar/SIMD 실행 시간은 이 바이너리의 관측 결과다.

따라서 **“SSE2/no-AVX host”는 부정확한 표현**이다. no-AVX는 측정 바이너리의 활성 target feature를 가리킨다. CPU에 AVX가 없어서 추가 성능이 나오지 않았다고 설명할 수 없다.

확인 근거는 `/proc/cpuinfo`의 AVX/AVX2/AVX512 flags, `rustc --print cfg`의 기본 `sse/sse2/fxsr`, 원 측정 바이너리 자체가 기록한 `compiled_avx=false`, `compiled_sse2=true`이다. [`wide::f64x4`](https://github.com/Lokathor/wide)의 vendored 1.7.1 source도 AVX가 꺼진 target에서 두 `f64x2`로 표현한다.

이미 실행한 release 바이너리의 `CompactRateTable::rates_simd` 한 함수만 objdump로 확인했다. 주소 범위 0x2f210–0x2f7e0의 codegen에 **packed-double `mulpd` 28개와 `addpd` 21개**가 있고, AVX의 v-prefixed 또는 FMA 명령은 발견되지 않았다. 이는 정적 명령어 개수이며 branch별 동적 실행 횟수는 아니다. 런타임 instruction tracing을 새로 했다는 뜻도 아니다.

원 바이너리 SHA-256은 `affa4234974bfb17a321aa611a6ef702a6e05434043d9cb7f817ac0a20655e68`이다. 전체 명령과 함수 assembly는 `CODEGEN_REVIEW.json`, `COMPACT_RATES_SIMD_OBJDUMP.txt`에 있다.

unsafe에 대한 정확한 범위는 **새 rate receiver crate가 `#![forbid(unsafe_code)]`를 쓰고 wide의 safe API를 호출한다**는 것이다. dependency 내부의 intrinsics까지 unsafe가 없다고 주장하지 않는다. 새 코드와 재현 명령에 fast-math/FMA 옵션을 넣지 않았고, 검사한 함수에서도 FMA를 발견하지 않았다.

## 2. 관측 ref와 변경 계보의 중요한 차이

부모 단계 문서가 현재 관측 HEAD로 기록한 ref는 `8d0c79184e09efb5bdadc24a6315c60a71a44264`, BR06의 고정 과학 pin은 `a21d573980f66fe02891bd216153443b5352f921`이다. read-only GitHub compare API를 실제 호출한 결과:

```text
base = a21d573980f66fe02891bd216153443b5352f921
head = 8d0c79184e09efb5bdadc24a6315c60a71a44264
status = behind
ahead_by = 0
behind_by = 595
merge_base_commit = 8d0c79184e09efb5bdadc24a6315c60a71a44264
```

즉 **8d0는 a21의 595 commit 조상**이다. 현재 default ref에서 관측됐다는 사실을 더 새로운 작업의 tip이라는 뜻으로 해석할 수 없다. “최신 GMRES 구현으로 갱신했다/갱신 가능하다”는 표현은 이 비교로 뒷받침되지 않는다. 반대 방향 compare의 `files=[]`를 두 tree 전체가 같다는 뜻으로 읽어서도 안 된다.

실제 [8d0의 `crates/rodas5p-krylov/src/kernels.rs`](https://github.com/cosmosapjw-quantum/vigilode/blob/8d0c79184e09efb5bdadc24a6315c60a71a44264/crates/rodas5p-krylov/src/kernels.rs)를 받아 보존된 a21 source와 비교했다. **3,159 bytes가 완전히 같고**, SHA-256은 `4af9acb562e4072ef3526279c495444fbfcfb5147336cb778992fb82db7ad9e3`, Git blob SHA-1은 `e809b79d137c4e94b959aae92f7f5df878ea2195`로 API 응답과도 일치했다.

8d0에서 `crates/rodas5p-fair-ab/src/paired_timing.rs`를 요청한 결과는 **404**였다. 그 ref의 해당 파일 내용을 읽었거나 적용했다고 주장하지 않는다. 확인 가능한 paired timing source는 보존된 a21 파일이며 SHA-256은 `3978924ea5f6527fb4335bd04e52650e5f117af50404cdae4d5f5e1ec8df1520`이다. GitHub 요청·응답은 `VIGILODE_COMPARE_A21_8D0.json`, `VIGILODE_8D0_KERNELS.json`, `VIGILODE_8D0_PAIRED_HEADER.json`에 그대로 남겼다. 대량의 다른 원본이나 595개 commit patch를 다시 받지 않았다.

## 3. 실제 재사용과 이번 작업에 맞는 범위

| 기능 | source에서 확인한 역할 | 이번 적용 판단 |
| --- | --- | --- |
| `dot`, `axpy`, `scale` | 일반 slice 벡터 연산과 orthogonalization counters | 4항 × 15채널의 고정 양의 합은 전용 고정 배열 평가가 직접 대응한다. 계수 보간을 orthogonalization work로 세지 않는다. |
| `linear_combination_into` | `Vec` column과 coefficient의 일반 선형 결합, shape 검사 | 재사용 가능한 수학 패턴이다. 현재 고정 4×16 배열을 동적 column 표현으로 바꿀 필요나 성능 이득은 검증되지 않았다. |
| two-pass MGS / GMRES 계보 | basis 직교화와 선형 연립계 반복해법 | scalar T에서 15개 k(T)를 평가하는 일에는 풀 선형계가 없다. 이 호출을 GMRES로 바꿀 근거가 없다. |
| paired timing | warmup, ABBA, session/A–A 통제, 분산을 반영한 판정 | 이번 새 모듈은 측정 원칙을 채택했다. VigilODE timing 소스 자체를 이식하거나 formal promotion gate 통과를 주장하지 않았다. |

큰 반응망에 대한 implicit solver를 새로 만들 때는 VigilODE의 Jacobian/operator, Krylov workspace, residual/출력 오차 계약을 별도 DAG에서 활용할 수 있다. 그 작업에는 positivity, species budget, 열·화학 에너지, CX splitting 및 timestep 제어기의 대응을 검증해야 한다. 이번 최적화에서는 원 제어기·half-flow를 유지한다는 사용자 조건과, 단순한 T-only 계수 평가라는 실제 연산에 맞추어 적용 범위를 정했다. solver의 일반적인 성능 평판만으로 해당 조건을 통과한 것으로 취급하지 않는다.

## 4. 속도 관측과 VigilODE의 confirmatory gate

a21의 `paired_timing.rs`는 최소 2 warmup, 30 pairs, **6 독립 sessions**, 10,000 bootstrap resamples, 95% confidence, required speedup 1.15, 대응하는 A/A session·noise 검사와 Monte-Carlo gate를 요구한다. rate kernel의 6 ABBA blocks는 독립 process 6개라는 뜻이 아니다. native RHS의 독립 process 5개도 그 formal 6-session 요구를 충족하지 않는다.

따라서 이번 수치들은 **명시된 동일 입력·정확도 조건의 bounded wall-time 관측**으로 보고한다. “VigilODE confirmatory performance gate PASS” 또는 환경 일반적 우월성으로 승격하지 않는다. scalar/SIMD의 작은 native RHS 차이는 A/A 분산과 함께 해석하며, 이번 codegen 검토를 근거로 새 AVX 실행의 속도를 예측하지 않는다.
