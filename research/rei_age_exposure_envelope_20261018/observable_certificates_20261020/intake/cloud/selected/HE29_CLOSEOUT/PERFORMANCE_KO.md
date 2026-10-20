# HE29 최적화: 실제 성능과 채택 결정

2026-10-20의 새 측정이다. **채택한 NCP 경로는 순차 packed Rust JVP(1 thread)**다. 새로운 물리 solver나 원래 네 기준해의 교체가 아니다. 네 쌍이 모두 인정된 뒤 단일 r4/table512 optional canary에서만 사용한다.

## 1. Jacobian 조립

실제 원래 `Model.jac`를 baseline으로 호출했다. HE29 m8/GL4/q0의 원래 광자 geometry와 rates를 사용하되, 다섯 gas RHS 호출에는 제조한 affine 함수를 넣어 조립 비용을 분리했다. 원래 LIL 대입과 새 canonical CSR의 `data/indices/indptr`가 세 크기에서 정확히 같았다. warm-up 뒤9라운드, 각 함수3호출 평균, baseline/candidate 순서를 번갈아 측정했다. speedup은 각 paired ratio의 median이며 두 median 시간의 비율과는 다를 수 있다.

| r | K / 전체 차원 | 원래 LIL median ms | 새 CSR median ms | paired median 가속 | 원래 tracemalloc peak B | 새 CSR peak B | peak 감소 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 512 / 535 | 12.7664 | 1.7152 | 8.3455× | 495,391 | 326,006 | 34.19% |
| 4 | 640 / 663 | 14.2654 | 1.7512 | 8.7024× | 639,666 | 403,141 | 36.98% |
| 8 | 896 / 919 | 19.9328 | 2.3503 | 8.7804× | 908,988 | 559,318 | 38.47% |

`tracemalloc`은 이 조립 호출에서 관찰한 Python/NumPy allocation이며, 전체 RSS나 source-table memory가 아니다. packed 값만 보관하는 양은 K512/640/896에서66,272/82,656/115,424 B다. 최초 cProfile K640은 LIL `__setitem__` 7,684회, 그중 scalar7,680회를 확인했다. profile의 계측 시간으로 speedup을 계산하지 않았다.

최초 조립 snapshot의 source hash와 raw rounds는 `evidence/ASSEMBLY_PROFILE_FIRST.json`에 있다. 이후 `lam>=0`라는 추가 검사를 제거해 원래 finite trial domain을 보존했다. 계수 계산·배열 조립은 바뀌지 않았고 최초 benchmark의 rates는 비음수였다. 이 작은 검증 분기 삭제를 최종 파일 전체의 새 timing이라고 주장하지 않으며, 해당 최초 측정치를 재사용한다.

## 2. 실제 ABI2 합성 IVP의 전체 적분 호출 시간

고정 Jacobian을 가진 비자율 제조계 \(F(t,y)=J(y-y_*(t))+y_*'(t)\)를 사용한다. \(y_*(t)=S(b+a\sin t)\)는 알려진 해다. gas4, photonK, passive ledger19의 구조와 원래 행 순서를 사용하며 모든 성분을 기존 error norm에 유지한다. 고정 계수는 양쪽 모두 이미 준비돼 있으므로 source table/새 물리 Jacobian 생성 비용은 포함하지 않는다. 이것은 HE29 native throughput 측정이 아니다.

동일 라이브러리·VigilODE solver·rtol1e-10·scaled atol1e-12·출력[0,1]·max step·initial step을 사용했다. 세 K마다 네 모드(legacy CSR1, packed1/2/4)를 warm-up하고, 실행 순서를 회전하며7라운드 측정했다. 매 라운드 endpoint의 uint64 비트와 attempt 수를 baseline과 대조했다.

| K / 전체 차원 | Python–CSR1 median s | packed1 median s | packed2 median s | packed4 median s | packed1 paired 가속 |
|---:|---:|---:|---:|---:|---:|
| 512 / 535 | 0.397504 | 0.272739 | 0.443686 | 0.630383 | 1.5324× |
| 640 / 663 | 0.438953 | 0.291633 | 0.451497 | 0.616139 | 1.4986× |
| 896 / 919 | 0.549691 | 0.399713 | 0.587548 | 0.734229 | 1.3787× |

모든 비교의 endpoint 비트가 일치했다. 해석해 대비 최대 scaled 절대오차는 각 K에서1.450106701383902e-11 /1.4423351402115259e-11 /1.4369283540816014e-11이다. 이는 제조계의 검산 오차이고, 물리 fraction gate 또는 기체온도 오차가 아니다.

| K | attempts | 기존 foreign JVP | packed foreign JVP | 실제 Rust JVP | prepare | exact-state cache hits | packed workspace B |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 512 | 14 | 4946 | 0 | 4946 | 14 | 4932 | 79,112 |
| 640 | 14 | 4946 | 0 | 4946 | 14 | 4932 | 98,568 |
| 896 | 14 | 4923 | 0 | 4923 | 14 | 4909 | 137,480 |

같은 callback 객체를 두 번 사용하는 새 회귀 경로도 세 크기에서 통과했다. 각 호출의 prepare delta를 비교하며 lifetime count와 혼동하지 않는다. 기존 opaque native chemistry 호출을 줄였다는 주장은 하지 않는다. 이 표의 `native_jvp`는 **Rust kernel 연산**이며 HE29 원본 native owner 호출은0이다.

## 3. 경량화·벡터화·병렬화의 범위

- NumPy 배열 연산으로 많은 Python sparse 삽입을 없앴다. fixed storage와 미리 할당한 scaled direction/workspace를 Rust에 보관해 매 JVP의 Python callback·CSR metadata 순회를 줄였다.
- 같은 Jacobian을 재사용하는 조건은 정규화 시각과 모든 scaled-state 비트의 정확한 일치다. interval마다 cache를 새로 만든다. Jacobian을 근사적으로 오래 쓰거나 FD4열을 생략하지 않는다.
- Rayon1.12.0의 local pool을 실제로 사용해 독립 photon output 행만1/2/4 worker로 처리했다. 한 행의 reduction은 원래 gas-first 뒤 photon 순서다. parallel sum·fast-math·FMA 재결합·정밀도 축소는 도입하지 않았다.
- 이번 환경에서 packed2는 packed1보다1.47–1.58배, packed4는1.78–2.24배 느렸다(paired median speedup의 역수). 이 결과에 따라 NCP 기본값을1로 고정한다. 특정 CPU instruction의 SIMD 발생은 계측하지 않았으므로 하드웨어 SIMD 가속을 주장하지 않는다.
- K가 작은 행 작업에서 worker scheduling의 비용이 이득을 넘었을 가능성은 있으나, 그 비용 자체를 따로 profile하지 않았으므로 원인 확정으로 쓰지 않는다. 현재 결과는 동일 workload의 실행 시간 비교다.

실행 환경은 Python3.12.14 /NumPy2.3.5 /SciPy1.17.0 /Rust1.94.1, `cpu.max=800000 100000`(8CPU 상당 quota), affinity9CPU다. numerical BLAS/OpenMP thread는1이다. shared sandbox의 시간 측정이며 NCP의64CPU 성능으로 외삽하지 않는다. 상세 플랫폼, affinity, source/library SHA, round별 시간과 telemetry는 `evidence/PAIRED_FFI_FINAL.json`에 있다.

## 4. 총 실행 시간에 대한 판단

조립 가속8.35–8.78배와 합성 적분 가속1.38–1.53배는 **서로 다른 비용 실험**이므로 곱하지 않는다. 어떤 한 구간이 전체 시간의 f이고 그 구간만 s배 빨라진다면 총 가속은 \(1/((1-f)+f/s)\)이다. 실제 HE29에서 f를 결정하려면 원래 native RHS·source-table 구성·Jacobian·GMRES 비용의 실제 반환이 필요하다.

현재 NCP 실행이0/4이므로 native gas 비용이 우세한지, source table이 우세한지 확정하지 않는다. 새 kernel은 준비됐고, 원래 네 Radau+DOP853 기준해를 먼저 확보한 뒤 동일 binary/table의 단일 canary로 비교할 수 있다. native throughput과 전체 transport memory는 `NOT_MEASURED`다.

## 5. 게시·백업과 검증 경계

첫 게시 `8cb0ebb91a78d2f1b751caa1c3ffc5d170ddfe41`는 19개 파일의 실제 Git readback이 일치했다. 최종 ABI2 코드는 `a5d4711460c09b310b78c9692aa62534b7a843d3`로 게시했고, 82개 파일을 Git에서 다시 읽어 바이트와 SHA256 일치를 확인했다. 완전 보존 묶음 `77f1c73e`는 Drive와 Dropbox 양쪽의 raw-byte 다운로드 및 내부 91개 payload 해시 검증을 통과했다. 정확한 identity와 후속 문서 closeout은 `DELIVERY.json`과 `evidence/` 영수증을 따른다.

별도의 clean Git checkout에서 게시된 NCP 빌더도 실제 실행했다. Cargo 컴파일은 146.650초에 성공했고, 과학·solver·test 실행은 없었다. 새 library SHA `802190605e7b5e175f36d1d986e2a203c1835fbd6a39571895481b8efe9a92b4`는 이 보고서에서 측정한 library SHA `8299915d8490e958fbebe54d253d98c98b1b932a50e8640398ad4ec274abf434`와 다르다. 소스 5개·toolchain·flags는 같지만, 서로 다른 rebuild artifact로 보존했다. 정적 경로·ELF layout 차이를 기록했으며, 모든 기계어 차이의 원인이나 새 바이너리의 수치 동등성을 별도로 주장하지 않는다. NCP는 자신의 build receipt와 library를 사용한다.

기존 HE28 pilot 및 6/6 study, HE29 90/720 및 50개 tests, 기존 VigilODE 96/3/Schur23은 재실행하지 않았다.
