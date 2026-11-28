# C2c 독립 검토

판정은 **ACCEPT_SCOPED_SMALL_R_SCALED_SEQUENCE**다. 사전 등록한 세 개의 작은 R 지점에서 공간·적분 오차의 raw 및 scaled 기준, 한 지점의 독립 구면 앵커, 여섯 fixed-m 상태 연결, 네 native/reference 비교가 모두 통과했다. 이는 유한 수열의 경험적 수치 검증이며 전체 C2, 연속공간 오차 상계 또는 점근 remainder의 정량적 인증이 아니다.

검토자는 새 고유값 계산이나 물리 적분을 실행하지 않았다. 원래 분석 모듈을 import하지 않는 표준 라이브러리 전용 `C2C_INDEPENDENT_REVIEW_RECALCULATE.py`로 완료된 결과의 스칼라와 identity를 별도로 재계산했다. 검토 JSON에는 계약·실행 소스·DATA·최종 분석·검토 코드의 SHA-256을 기록했다.

## 확인한 수치

| x=R/a_A | S=Lbar_O/x³ | 극한 계수 4√2/15와의 관계 |
|---:|---:|---|
| 0.125 | 0.2852412698673968 | 아래에서 접근 |
| 0.0625 | 0.3251710273598622 | 아래에서 접근 |
| 0.03125 | 0.3494330529056764 | 약 7.34% 작음 |

새 세 지점의 네 기저 설정 전체에서 최대 scaled direct–force 차이는 2.27061×10⁻⁹, 최대 scaled h/p/tail 차이는 2.65547×10⁻⁹다. 두 연속 적분 차수 증가와 마지막 세 수준의 연산자 검사를 각각 확인했다. 원점 항의 상쇄와 force 차분의 상쇄를 기록하되 이를 인증된 roundoff 상계로 해석하지 않았다. 작은 generalized eigen-residual도 연속공간 파동함수 또는 coupling 오차의 상계로 사용하지 않았다.

x=.125의 독립 구면 앵커는 prolate와 scaled 차이 4.23948×10⁻⁷, l72→96 증가량 3.76672×10⁻⁷이다. 등록된 앵커 기준은 본체 spatial 기준보다 느슨하며 한 지점만 검증한다. 구면 표현의 p는 radial derivative에서 직접 계산했고 Δd로 대체하지 않았다. 구면 원점 변환식 자체의 일치는 구성상 identity이므로 독립 물리 검산으로 중복 계산하지 않았다.

여섯 상태 연결의 최소 normalized overlap은 0.99854924745495, 최대 차수 증가량은 6.66134×10⁻¹⁶이다. 양방향 overlap과 자기 노름도 마지막 세 차수에서 통과했다. 누적 위상은 모든 지점에서 +1이다. 이는 각 fixed-m local 연결의 검산이고 hidden crossing이나 rank-five cluster의 격리 인증이 아니다. 네 parity 비교의 최대 raw 차이는 1.55431×10⁻¹⁵다.

## 실행과 식별성

MAIN 16개, FOLLOWUP 24개 작업을 각각 원래 manifest와 대조했다. 40개의 RESULT/DATA, 생성된 상태 archive, TASK_EXECUTION, 실행 당시 소스 snapshot의 SHA-256과 크기 및 native identity 연결을 확인했다. 새로 선택한 고유상태는 prolate 24개와 구면 4개, 합계 28개다. 구면 작업은 각각 두 Ritz root를 요청했으므로 요청 root 수는 8개이며 선택 상태 수와 구별했다. fallback과 실패한 물리 작업은 없었다.

실제 실행은 두 rank 중 worker 한 개, OMP/BLAS thread 한 개였다. 두 배치 wall 합계는 320.102636초, 관측 최대 RSS는 548.347656 MiB다. 두 배치 모두 preflight, 소스 불변, 소유 프로세스 정리를 통과했고 OOM 관련 counter 증가는 0이었다. memory.max event 증가는 한도 접근·회수 압력을 나타내며 OOM 발생과 동일하지 않다. NCP 64코어 실측 또는 speedup은 검증하지 않았다.

cache credit은 raw-headroom 기본값을 유지한 명시적 opt-in이다. protected/dirty/mapped/shmem/unevictable 메모리를 제외하고 clean file cache의 절반만 가용량 추정에 반영한다. 조상 cgroup 및 host MemAvailable의 최솟값, 20% 여유, worker RLIMIT_AS를 유지했다. 이 추정량은 예약이나 미래 OOM 부재 보증이 아니다.

## 실행 전 발견 및 수정

1. 작은 x에서 기존 고정 절대 bright detectability floor는 실제 coupling의 x³ 감소를 잘못 실패로 분류할 수 있었다. 첫 물리 계산 전에 scaled resolution 기준으로 명시적으로 변경하고 이전 계약을 보존했다. raw 오차 허용치는 완화하지 않았다.
2. 배치 launcher process group만 종료하면 별도 session으로 실행된 과학 worker가 남을 수 있었다. registry gate, expected-parent death signal, rank 종료 cleanup 및 owned-process pidfd 정리를 추가했다.
3. 제조시험은 local PID와 외부에 mount된 /proc PID의 불일치를 실제로 발견했다. 기존 엄격 검사는 관계없는 프로세스를 신호하기 전에 차단했다. namespace inode와 NSpid/NSpgid/NSsid 매핑을 적용한 뒤 seven synthetic cleanup tests가 통과했다. 이는 물리 계산 전 환경 인터페이스 결함과 수정이며 과학 수렴 실패가 아니다.

계약과 구현은 위 수정 후 고정되어 물리 실행에 사용됐다. 소스 snapshot이 MAIN과 FOLLOWUP 당시 버전을 각각 보존하므로 후속 보고 코드 추가를 실행 당시 identity와 혼동하지 않는다.

## 유지해야 할 범위

가장 작은 x에서도 극한 계수와 7.34% 차이가 남는다. 이는 측정된 수치 refinement 차이보다 훨씬 커서 유한 R 보정이 분해되어 있다는 증거다. 유한 세 점의 단조 접근으로 Big-O 상수, 적용 반경 또는 더 높은 점근 차수를 정하지 않는다. 0.25 지점은 이전 두 차수 검증을 재사용한 문맥·연결점이며 이번 세 차수 신규 검증으로 소급 변경하지 않는다.

`scientific_PROMOTE=HOLD`, `full_C2_closed=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. 큰 R scaled 검증, 충돌에 필요한 R 범위, cluster와 continuum 문제는 별도 의존성이다. Git 게시와 외부 provider receipt 검증은 최종 전달 담당자의 작업이며 본 과학적 admission과 구별한다.
