# REI Bianchi 통합 최적화 연구 판단

## 목적과 판정 범위

오늘의 실행 목표는 non-tilted LRS collisionless Einstein–kinetic 고정 모형에서 matter/radiation의 독립 초기 응력을 갖는 175점 pilot과 z=20→2 시간발전을 확보하는 것이다. 성능 수치는 별도의 benchmarking campaign으로 측정하지 않는다. 이 문서의 최적화 판단은 실제 source와 재사용 가능한 계산의 구조에 근거한다. elapsed/CPU 기록은 실행 provenance이며 speedup 측정이 아니다.

PR198의 8-state, 65-epoch, half-contraction 자료와 별도 pilot의 40/56-state, 121-epoch, Frobenius 자료를 독립적으로 보존한다. 같은 vendor 물리 source라는 사실만으로 두 실행을 같은 IVP로 합치지 않는다. AGE/VigilODE lane의 native convergence와 nonlinear Grackle 판정은 바꾸지 않는다.

## 실제로 채택한 계산 절감

| 선택 | 구현 또는 저장 근거 | 줄이는 작업 | 범위와 한계 |
|---|---|---|---|
| 기존 결과의 원자료 재사용 | A의 625+606, B의 원래 91+3 raw 및 receipt | 완료된 IVP 재적분 | 원자료 hash와 실제 물리/config identity가 일치하는 경우만 |
| 175점 중 35개 exact reference | B 원래 grid와 component contract 교집합 | 35개 초기구간 적분 | 기존 wrapper의 실행 identity를 새 wrapper로 바꾸지 않음 |
| endpoint full-state continuation | B 원래94+신규143의 40/56 상태, metric와 시간 누적값 | z20→4 prefix의 반복 | z4→2는 새로운 수치 구간이며 별도 receipt/검증 필요 |
| worker별 immutable matrix cache | recovered adapter.py의 cached_matrix와 전체 인자 key | Legendre transport 행렬의 반복 구성 | 행렬 연산식과 원 vendor RHS는 유지 |
| worker별 canonical momentum cache | adapter.py momentum cache, component_adapter.py calibration cache | 동일 resolution/amplitude의 packet setup | 실제 moment는 각 geometry에서 계산; 진화값을 잘못 재사용하지 않음 |
| bounded matrix diagnostics | brightness moments @ Legendre basis, NumPy packet moment reductions | epoch/angular 진단의 Python 내부 반복 일부 | 모든 time/trajectory/packet을 한 거대 array에 모으지 않음 |
| 지속 worker와 독립 trajectory 병렬화 | recovered cooperative supervisor + 새 phase dispatch | 매 case process startup 및 반복 imports | solver 내부를 무리하게 병렬화하지 않고 독립 IVP를 분배 |
| BLAS/OpenMP 1 thread | import 전 OMP/OPENBLAS/MKL/NUMEXPR/VECLIB=1 | worker×BLAS nested oversubscription | 실제 실행 receipt에 environment 보존 |
| case checkpoint와 hash 확인 resume | INPUT/ATTEMPT/RESULT/raw, 고정 phase 경로 | 중단 뒤 완료 case의 반복 | failed/incomplete attempt 자동 재시도 없음; budget 누적 |

위 항목은 authoritative source 재사용과 필요한 작업량 축소에 관한 판단이다. 기존 코드 대비 wall-time 배수, 강한 확장성 또는 NCP64-core 효율을 측정했다고 주장하지 않는다.

## 후보별 재사용 결정

| 조사한 후보 | pin 또는 lane | 이번 채택 판단 |
|---|---|---|
| canonical FV massive moments, LRS radiation hierarchy | PR147 3b85dedce84d37b3e165da00685a8a984950aafe | exact vendor source와 현재 adapter/cache 재사용 |
| PR198 reduced 8-state common radiation energy | reviewed b140170ce0c58159368b6b81be49ac35ca764851 | 완료된 A 분석과 그림에 그대로 재사용. B의 40/56-state 실행 identity를 바꾸는 신규 reduction은 이번 범위에서 불필요 |
| PR213 cooperative shared executor | d32cd99fa19c65aa1ca63dbc8aab8741834270e8 | 실제 resource admission/child ownership 개념을 대조. 이미 복구한 B supervisor가 필요한 기능을 제공하여 별도 backend 교체 불필요 |
| RUN19, fastest-track, PR208/210 | BRANCH_RECOVERY_VERDICT.json의 실제 pin | native transport/성능 lane의 provenance만 연결. Python collisionless solver의 RHS와 섞지 않음 |
| VigilODE directed/damped kernels | productionplan cc2e1a009ac6802ef01a289392e9715074a882ba; BR06 a21d573980f66fe02891bd216153443b5352f921 | AGE stiff/native lane에 관련. 오늘의 작고 비강성인 DOP853 pilot을 다른 solver로 치환할 근거 없음 |
| 새 C++/GPU/JIT backend, 거대 batch ODE | 해당 없음 | 출처·수치 동등성 검증 비용이 당일의 미완료 143개+tail 목적보다 큼. 이번에는 도입하지 않음 |

## 64-core / 128-GB NCP에서의 실행 정책

현재 NCP의 CPU affinity, cgroup, available memory, disk와 process load는 관측하지 못했다. 로컬 SSH key 부재와 현재 Desktop Commander의 명시적 재시도 금지 quota 응답을 기록했다. 이전 세션의 실패를 영구 blocker로 간주한 것이 아니다. 이 turn의 Python과 C++는 모두 실제 실행 PASS이며 sandbox 가용 자원에서 연구를 진행한다.

준비된 wrapper는 실제 affinity와 cgroup quota를 합쳐 effective CPU를 계산한다. 허용된 CPU의 /proc/stat에서 idle 비율을 관측하고, available memory와 cgroup limit을 함께 반영한다. 120GiB 이상의 관측 memory에서는 16GiB 여유를 둔다. 0.5GiB/worker를 보수적 admission 단위로 사용하고 max63 workers로 제한하여 controller에 여유를 남긴다. 상한은 실제 사용 수나 과학적 실행 허가를 뜻하지 않는다.

다른 연구 process가 바쁘다는 이유로 전면 중단하지 않는다. memory가 허용하면 최소 한 개 nice worker로 진행하며, 여유가 늘면 병렬 slot을 늘린다. 자신의 worker만 관리하고 다른 process를 종료하지 않는다. 사용자 요청과 일치하게 기존 owner checkout의 dirty/untracked 상태를 초기화하지 않는다.

B1과 B2는 각각 고정 output 경로, 누적 child/controller envelope, case deadline을 갖는다. completed case는 raw 확인 뒤 reuse하고 pending만 실행한다. sandbox에서 이미 완료한 동일 case를 NCP 활용 목적만으로 다시 돌리지 않는다. NCP가 다시 가용해져도 새로운 과학 질문 또는 실제 pending case가 있어야 실행한다.

## 연구 가설과 반증 조건

1. **setup caching이 계산의 물리를 바꾸지 않는다 — implementation-verified.** source matrices와 RHS를 바꾸지 않고 전체 인자 key에 따라 저장한다. mutable geometry/solution을 cache하면 이 판단은 성립하지 않는다.
2. **case 병렬화가 독립 IVP의 결과를 보존한다 — implementation-verified, 새 raw는 실행 후 별도 판정.** case별 state/source/config가 분리되어야 한다. 공유 mutable state나 누락 receipt가 있으면 해당 case를 완료로 인정하지 않는다.
3. **full-state z4 continuation이 같은 IVP의 후반부다 — derived + 실행 후 numerically checked.** saved endpoint의 전체 상태와 cosmology/normalization을 보존해야 한다. 순간적인 Sigma/Pi 두 숫자만으로 restart하는 것은 이 주장을 지지하지 않는다.
4. **초기 total anisotropic stress cancellation은 이후 shear를 제거하지 않는다 — literature-supported 구조 + derived local result.** 서로 다른 redshifting과 anisotropic work가 matter/radiation 응력을 다르게 바꾼다. 고정 quadrupole 모형에서 초기 곡률은 S''=-(1-B_m)P_m이며 B_m=0.031700764390593536. 이 식은 국소 주장이고 보편적 endpoint 선형법칙은 아니다.
5. **NCP64 성능 우월 또는 특정 speedup — unresolved / not benchmarked.** 실제 hardware 관측과 비교 실험을 수행하지 않았으므로 수치 성능 주장을 하지 않는다.

## 근거

- 저장 source: adapter.py, resources.py, components/component_adapter.py, components/unified_pilot.py, vendor/canonical_fv.py.
- 물리 및 norm 대응: PHYSICAL_CONVENTION_ADAPTER.md, PHYS_MATH_CONTRACT_REVIEW.json.
- 분기 조사: evidence/BRANCH_RECOVERY_VERDICT.json.
- canonical momentum와 reflection symmetry: Heinzle–Uggla, https://arxiv.org/abs/gr-qc/0512031 .
- massive LRS collisionless dynamics: Rendall–Uggla, https://arxiv.org/abs/gr-qc/0005116 .
- anisotropic matter evolution: Calogero–Heinzle, https://arxiv.org/abs/0911.0667 .
- DOP853 interface: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html .
- numerical library threading: https://docs.scipy.org/doc/scipy/tutorial/parallel_execution.html .

이 문서는 source/contract 판단이다. 최종 new-case 수, raw 검증, 실제 그림 감사와 provider receipt는 UNIFIED_STATUS.md 및 UNIFIED_DAG.json의 최신 판정으로 보완한다.
