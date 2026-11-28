# C2c 작은 R scaled coupling 수치 검증

## 판정과 범위

**SCOPED_SMALL_R_SCALED_SEQUENCE_CONVERGED.** 새 세 지점의 h/p/q/tail 검증, 독립 구면 앵커, 여섯 fixed-m 연결과 네 구현 비교가 사전 기준을 모두 통과했다. 이것은 등록한 유한 수열의 경험적 수치 검증이다. 연속체 오차의 엄밀한 상계나 R→0 극한의 수치 인증은 아니다. full C2=false, scientific_PROMOTE=HOLD, Eq55=NOT_RUN, production 기본값 변경 미승인을 유지한다.

전하 (Z_A,Z_B)=(1,2), x=R/a_A, E/E_A, Lbar=L/(−iℏ), pbar=a_A p/(−iℏ), dbar=d/a_A를 쓴다. ℏ를 1로 놓은 물리 명제가 아니라 명시적으로 무차원화한 계산 값이다. O는 공통 전하중심이고 B 원점과 Lbar_O=Lbar_B+(x/3)pbar 관계를 쓴다. 최저 m=0 상태와 밝은 |m|=1 상태의 위상 규약은 부모 연구와 같다.

## 수치 결과

S(x)=L_O/(−iℏx³), A2의 해석적 극한 계수 C=4√2/15=0.377123616632825다.

| x | Lbar_O | S(x) | (S/C−1) | 증거 |
|---:|---:|---:|---:|---|
| 0.03125 | 1.06638504915e-05 | 0.349433052906 | -7.3426% | 새 계산 |
| 0.0625 | 7.93874578515e-05 | 0.325171027360 | -13.7760% | 새 계산 |
| 0.125 | 0.00055711185521 | 0.285241269867 | -24.3640% | 새 계산 |
| 0.25 | 0.00357649378436 | 0.228895602199 | -39.3049% | C2a 재사용 |

x를 줄인 이번 수열은 C에 가까워진다. 가장 작은 점에서도 유한-R 차이는 7.3426% 남는다. 그 차이는 아래에서 관측한 기저 증가 차이보다 훨씬 크다. 이를 특정 수렴률, 미지 remainder 상수, 10% 점근 적용반경 또는 외삽 계수 인증으로 바꾸지 않는다. A2에서 유도한 Lbar_O=Cx³+O(x^(7/2))의 remainder 상수와 유효 반경은 여전히 미지다. 계수를 fitting하지 않았고, 단조성이나 특정 감소율을 통과 조건으로 쓰지 않았다.

## 오차 검사

최대값은 새 세 지점의 네 profile 전체에서 취했다. 아래 차이는 경험적 일치·안정성 검사이며 엄밀 오차 enclosure가 아니다.

| 검사 | 관측 최대 | 사전 기준 |
|---|---:|---:|
| h/p/tail의 scaled L_O 차이 | 2.65547268e−9 | 2e−6 |
| direct 적분 두 연속 증가량 /x³ | 2.00239825e−12 | 1e−8 |
| force 적분 두 연속 증가량 /x³ | 2.25930386e−14 | 1e−8 |
| direct–force의 terminal 3×3 비교 /x³ | 2.27060909e−9 | 1e−7 |
| momentum 오차가 유발한 scaled L_O | 1.86939057e−9 | 1e−7 |
| 원점 항등식 오차 /x³ | 1.36424205e−12 | 1e−7 |
| norm 오차 | 8.88178420e−16 | 1e−10 |
| 이산 고유방정식 상대 residual | 4.68561267e−15 | 1e−9 |
| dark coupling 절댓값 | 7.91889124e−22 | 1e−12 |

기본 d7, radial64/angular40, Hamiltonian q12, 물리 extent30을 썼다. h는96×60, p는d9/q14, tail은 내부64개 구간을 정확히 보존하고 extent40까지16개 구간을 추가했다. direct q=16/24/32, force q=12/20/28 모두 마지막 세 차수의 두 증가량을 검사했다. 더 높은 q나 더 미세한 quartet fallback은 **0회**다. x=.25는 부모의 두 차수 자료를 재사용했으며, 새 세 차수 확인으로 표시하지 않았다.

p는 실제 미분 연산자로 평가하고 ΔE·d와 독립 비교했다. 원점/운동량 scaled 식은 각각 |Lbar_O−Lbar_B−xpbar/3|/x³ 및 |pbar−ΔE dbar|/(3x²)다. tail 내부 knot는 두 상태 모두 bitwise 같은 배열 prefix다.

물리 계산 전에 작은 신호 검출 규칙만 명시적으로 조정했다. 부모의 절대 Lbar_O>2e−5는 x³로 사라지는 신호에 적합하지 않아, 양의 신호와 10x³×(scaled spatial 허용값) 초과 조건으로 대체했다. 원래 raw 오차 기준은 유지했고 새 scaled 오차 기준을 추가했다. 이 변경은 CONTRACT의 실행 전 이력에 있으며 결과를 본 뒤 조정하지 않았다.

## 독립 구면 앵커와 연결

x=.125, B 중심의 독립 구면 partial-wave 표현에서 lmax72/96, radial elements56, d4, Hamiltonian q14, rmax24를 썼다. 두 m sector마다2 Ritz roots를 요청하고 최저 상태만 보존했다. 관측량 q14/22/30에서 직접 angular generator 및 radial-derivative momentum을 평가했다.

- l96–prolate의 scaled L_O 차이: 4.23947674e−7 ≤ 1e−4.
- l72→l96의 scaled 증가량: 3.76672496e−7 ≤ 2e−5.
- 최대 energy 차이: 4.91300325e−8 E_A ≤ 1e−5 E_A.
- 구면 q 증가량, norm/residual, momentum/origin도 통과했다. 구면 원점 관계는 구성 항등식이며 별도의 독립 물리 검증으로 세지 않는다.

구면 precision 기준은 주 계산보다 느슨한 독립 표현 sanity check로 결과 전에 고정했다. 이것이 주 계산의2e−6 scaled spatial 기준을 대체하지 않는다. 구면 fallback은0회다.

x=.03125→.0625→.125→.25의 m=0/1 여섯 연결을 공통 O의 실제 공간 적분으로 계산했다. q16/24/32 두 증가량의 최대는6.66133815e−16, 양방향 차이 최대도6.66133815e−16, self-norm 오차 최대4.44089210e−16이다. 최소 normalized overlap은0.99854924745495이고 모든 누적 위상이+1이다. 이는 국소 fixed-m 연결이며 숨은 crossing 또는 rank-five 고립 인증은 아니다.

네 parity 사례의 raw 최대 차이는1.55431223e−15 ≤1e−11, scaled L_O 최대 차이는2.48634446e−13 ≤1e−8이다. 동결 x=.25의 기존 전체 적분/새 stream native, 새 최소x의 Python/native direct와 force, 첫 m0 연결의 Python/native를 비교했다. Bitwise 일치는 요구하거나 주장하지 않았다.

## 계산 구현과 실제 자원

Fortran real64/OpenMP/SIMD hot kernels 및 OpenMPI 독립 task 분배를 유지했다. fast-math, 재결합, FMA contraction, 숨은 mixed precision 및 암묵적 backend fallback은 사용하지 않았다. 세 native library의 ABI·바이너리·빌드 provenance를 실행 시 고정했다. 새 direct 경로는 동일 Gauss 점/가중치/순서를 최대32 patch씩 평가하고 batch scalar를 math.fsum으로 합친다. 전체 영역의 큰 임시 배열을 만들지 않는다.

실제 호스트는 CPU quota8, affinity9, cgroup memory8 GiB다. 사전 검사 후 MPI2 ranks(제어1+계산1), OMP/BLAS1 thread, worker 주소공간1.5 GiB, task240초를 적용했다. 전체40 tasks, 선택 상태28개(12 prolate pairs+4 sphere states), 구면 요청 Ritz roots8개, 두 batch wall 합계 **320.103초**, 최대 worker RSS **548.348 MiB**다. 등록 wall1800초 및 개수 제한 안에 끝났고 실제 실패 task·timeout·fallback은0이다.

메모리 사전 검사의 기본 raw-headroom은 유지했다. 이번에는 명시적 clean-file-half-v1 정책으로 보호되지 않은 clean file cache 후보의 절반만 회수 가능 추정량에 포함하고20% reserve를 적용했다. 이는 커널의 회수 보장이나 메모리 예약이 아니다. memory.max 이벤트는 MAIN에서289 증가했지만 OOM/OOM kill은 두 batch 모두0이다. 관련 공식 정의는 [Linux cgroup v2](https://docs.kernel.org/6.18/admin-guide/cgroup-v2.html), 정책 식·스냅샷은 provenance/MEMORY_DIAGNOSTIC.json 및 각 PREFLIGHT에 있다. 커널/cgroup 설정은 바꾸지 않았다.

과학 실행 전 timeout 제조시험에서 local PID와 /proc PID namespace 차이를 발견했다. 소유 token·namespace·start-time 검증, pidfd, registry gate, 부모 사망 처리로 수정했고 동일7개 시험이 통과했다. 이때 무관한 프로세스 signal0, 과학 실행0이었다. 실제 두 batch는 source unchanged와 owned-process cleanup을 통과했다. 초기 실패 이력은 지우지 않았다.

사전 구현 시험45개(27+scaled11+cleanup7), 추가 continuation/parity scalar9개 및 anchor scalar8사례를 기록했다. 독립 검토는 별도 scalar 재계산과 입력/결과 identity를 확인한다. 실행 중 소스는 MAIN/FOLLOWUP_CODE_SNAPSHOT.zip에 각각 보존했다. 최종 분석·보고 파일과 실행 당시 identity를 구분한다.

이번320초는 서로 다른 연구 task의 총 wall이며 속도향상 배율이 아니다. 동일 workload 비교 반복은0회이고 NCP64 실제 scaling은 NOT_RUN이다. 로컬 bind-to none 예외를 NCP 기본 core binding으로 전파하지 않는다. NCP에서는 실제 topology/가용 메모리와 승인된 새 workload로 rank/thread를 결정한다.

## 다음 단일 연구

C2D_LARGE_R_SCALED_NUMERICAL_AUDIT로 이어간다. 현재 x=4,8,16 증거를 재사용하고, 큰 x의 iL_O/(ℏx)→32√2/243 및 −iL_B x²/ℏ→128√2/729를 각각 raw/scaled 기준으로 조사하는 새 계약을 먼저 작성한다. 다음 지점·기저·box/tail·독립 앵커·상태 연결·fallback·예산은 아직 실행 계약이 아니며 새 큰-R 계산은 하지 않았다. 전체 충돌 R 구간, rank-five cluster, continuum enclosure, D1/단면적은 남아 있다.

재현 입력과 상세 판정은 CONTRACT.json, evidence/FINAL_AUDIT.json, 원 DATA/STATE 및 review/에 있다. 원 논문 PDF는 이 공개 코드 묶음에 포함하지 않는다.
