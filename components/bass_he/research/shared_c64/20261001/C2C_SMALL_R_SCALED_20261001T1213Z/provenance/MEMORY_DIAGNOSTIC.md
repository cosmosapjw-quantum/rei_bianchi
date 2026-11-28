# C2c 메모리 사전검사 진단

관측 시각: 2026-10-01T11:52:18.305922+00:00. 실행 커널: 6.18.44. 판정은 `PAGE_CACHE_DOMINATED_RAW_HEADROOM_FALSE_NEGATIVE_FOR_AVAILABLE_MEMORY`다. 이는 기존 raw headroom 계산이 산술적으로 틀렸다는 뜻이 아니라, 파일 캐시를 모두 회수 불가능한 사용량으로 취급하므로 새 프로세스의 가용량과 다른 양을 보고한다는 뜻이다.

관측된 cgroup 한도는 8.000 GiB, 현재 사용량은 7.803 GiB다. 그중 `file`은 7.178 GiB, `anon`은 0.333 GiB, `kernel`은 0.288 GiB다. 캐시가 사용량의 92.0%다. `memory.min=memory.low=0`, `memory.high=max`, `unevictable=0`이고 lifetime `oom`, `oom_kill`, `oom_group_kill`은 모두 0이다. `memory.events:max`는 한도 접근 횟수이며 OOM 발생 횟수와 동일하지 않다. PSI 파일은 제공되지 않았다. 이 자료만으로 미래 OOM 부재나 예약된 메모리를 보장할 수 없다.

Linux 6.18의 [cgroup v2 문서](https://docs.kernel.org/6.18/admin-guide/cgroup-v2.html)는 `memory.current`의 계층별 사용량, 파일 캐시와 shmem 및 LRU 분류, 그리고 한도 도달 시 회수 후에도 줄일 수 없을 때의 OOM 동작을 설명한다. [메모리 개념 문서](https://docs.kernel.org/6.18/admin-guide/mm/concepts.html)는 저장장치에서 다시 읽을 수 있는 페이지 캐시를 회수 가능한 메모리로 분류한다. [proc 문서](https://docs.kernel.org/filesystems/proc.html)의 `MemAvailable`도 단순 free가 아니라 파일 LRU와 watermark 등을 반영한 추정량이다. 따라서 캐시를 적절히 제외한 가용량 추정은 한도를 우회하는 동작과 구별된다. 다만 active 파일 캐시의 회수는 재읽기 비용을 낳을 수 있다.

두 후보를 분리했다. `X=shmem+file_mapped+file_dirty+file_writeback+unevictable`로 두고, 중복 항도 일부러 중복 차감한다. 캐시 종류의 중복 합산을 이득으로 쓰지 않는다.

- clean-inactive 후보: `C=max(0,min(file,inactive_file)-X)`, credit=`C`.
- half-clean-file 후보: `C=max(0,min(file,active_file+inactive_file)-X)`, credit=`floor(C/2)`.

각 유한 한도 조상에 대해 `B=min(limit,max(0,limit-max(current_before,current_after)+credit))`로 계산하고, 전체 추정량은 모든 조상의 `B`와 host `MemAvailable`의 최솟값이다. 필수 통계 누락·비정상 값은 credit=0으로 처리해야 한다. slab·swap·shmem·dirty·writeback·mapped·unevictable 항에는 credit을 부여하지 않는다. half 비율은 추가 보수성을 위한 **명시적 공학 정책**이며 커널 공식이나 회수 보증이 아니다.

| 방식 | 가용량 추정 GiB | 20% 여유 후 GiB | 0.5 GiB controller + 1.5 GiB/worker 허용 수 |
|---|---:|---:|---:|
| raw headroom | 0.197 | 0.158 | 0 |
| clean inactive | 0.896 | 0.717 | 0 |
| half clean file LRU | 3.784 | 3.027 | 1 |

**clean-inactive 방식만 채택하면 현재 상태는 실행 차단이다.** half-clean-file 방식을 채택할 경우에도 raw 방식은 기본값으로 유지하고, 새로운 C2c 계약에서만 정책을 명시하여 소스·계약 identity에 포함해야 한다. 원래의 20% reserve, worker RLIMIT_AS, controller envelope는 그대로 둔다. 조상별 제한, 필수 통계 누락, dirty/shmem 큰 경우, 음수 clamp, host 한도, 기본값 유지 테스트가 필요하다. 새 사전검사 성공을 확인하기 전에는 과학 작업을 시작하지 않는다.

이 진단에서는 `/proc`와 `/sys/fs/cgroup` 읽기, 작은 산술 계산과 문서 확인만 수행했다. cache drop, `memory.reclaim`, 프로세스 종료, cgroup 이동·한도 변경, 과학 실행은 하지 않았다. 관측 원문과 프로세스 목록은 동반 JSON에 있다. namespace 안에서 보이는 RSS의 합은 shared page 중복과 비가시성 때문에 cgroup 총량을 대체하지 않는다.

## 채택된 구현과 읽기 전용 검증

후속 결정에서 `clean-file-half-v1`을 명시적 opt-in으로 채택했다. `raw-headroom` 기본값은 유지한다. `host_probe.py`와 `launch_ncp.py`에 정책 선택을 추가했으며, `--bind-to none`은 로컬 sandbox의 명시적 예외로만 선택할 수 있다. 기본값은 `core`다. 캐시 통계 또는 `memory.min/low`가 비정상이면 credit은 0이다. host `MemAvailable`가 없으면 opt-in 계수법은 실행을 차단한다.

표적 구현 테스트 13개가 통과했다. 실패한 preflight에서 `--execute`를 지정해도 subprocess를 호출하지 않는지 mock으로 확인했다. 실제 새 호스트 스냅숏의 raw 예산은 298729472 bytes, 캐시 고려 추정량은 4149469184 bytes다. 2 ranks(1 controller, 1 worker), OMP 1, worker 1.5 GiB 조건의 읽기 전용 판정은 `READ_ONLY_LAYOUT_PASS_NOT_EXECUTED`다. 실제 OpenMPI 또는 물리 계산은 수행하지 않았다. root가 새 실행을 시작하기 직전에 `launch_ncp --execute` 안에서 다시 검사해야 한다. 코드 SHA와 전체 호스트 출력은 JSON의 `implementation`에 기록했다.
