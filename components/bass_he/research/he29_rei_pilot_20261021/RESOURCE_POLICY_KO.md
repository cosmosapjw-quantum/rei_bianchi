# REI pilot shared runner 자원 정책

이 runner는 이번 고정 pilot만 실행한다. `RUN_READY.sh --dry-plan`은 실제 affinity/cgroup cpuset, CPU quota, MemAvailable/cgroup memory 잔여와 0.12초 이상 per-CPU busy 관찰을 출력한다. 기본 실행은 이미 유효하게 완료된 exact identity 결과를 재사용하고 pending case만 실행한다. 기존 HE29 실행은 호출하지 않는다. sandbox 최초 실행은 `./RUN_READY.sh --max-workers 2 --time-budget-seconds 60`으로 제한한다.

후속 matter/radiation 독립 초기조건은 explicit `--campaign split_pilot --out research/he29_rei_pilot_20261021/data/results/split_cases`로 선택한다(repo root 기준). CLI의 기본 output은 원래 cases 디렉터리이므로 split campaign에는 이 경로를 함께 지정한다. 기본 campaign은 원래28건으로 유지한다. split campaign은 새12건을 정의하고 후속 view가 원래6건을 경로/identity로 참조한다. 두 campaign의 고유 완료 수는40이며 둘 다 pending0이다. 새12건의 실제 실행은 교정된4GiB reserve와 최대2worker,30초 wall budget에서 완료됐다. 원래28건을 다시 실행하지 않았다. 명령을 다른 output root로 바꾸어 완료 DATA를 숨긴 뒤 중복 적분하지 않는다.

64 CPU/128 GiB는 상한 profile이며 실제 host 사양을 가정하지 않는다. CPU55를 제외하며 실제 quota와 cpuset 중 작은 한도를 사용한다. CPU reserve는 작은 할당에서1, 8CPU 이상에서2다. RAM reserve는 max(4GiB, actual total/8), 새 case budget은1GiB다. 활성 case budget도 추가로 차감하므로 admission은 보수적이다. 다른 Codex/science 존재 자체는 HOLD 조건이 아니다. 관찰 busy CPU 수와 실제 가용 RAM으로 새 admission을 줄인다.

공유 `/tmp/cosmosapjw_hpc64_cpu_leases/cpu_N.lock` flock은 C21K naming과 호환한다. 잠긴 CPU가 있으면 다른 CPU를 시도한다. lease는 협력 runner 사이에서만 배타적이며 미참여 job에 대한 hard reservation이 아니다. 작업 identity flock과 identity별 receipt path registry는 다른 output root에서도 중복 수행을 줄인다. registry 결과는 pilot의 source/input/gate/raw validator로 확인한 뒤에만 재사용한다. child는 CPU1개에 pin하고 BLAS/OpenMP/Rayon thread1 환경을 적용한다.

각 child 완료 후 lease를 반환하고 자원을 다시 관찰한다. 가용 자원이 없으면 무한 대기하지 않고 DEFERRED를 기록한다. campaign 시간 한도에서 자신이 만든 direct science child만 종료하고 TIMED_OUT 및 config/identity를 보존한다. science worker는 자손 process를 만들지 않는다. 다른 job을 signal하지 않는다. 정상/실패 raw 결과는 pilot writer가 보존하고 runner는 exitcode와 과학적 completed validator를 함께 본다.

## helper provenance

`vendor/resources/c21k_scheduler.py`: bass_cr commit `bab323983dad5206e162dbfdaefc167f2fabea45`, 원본 scheduler.py SHA256 `495f469faf432cba3764781e545d5711b7ba4f652c778b3aaa57589c64f04928`. byte 그대로 vendor. 호출 함수는 `resource_snapshot`, `acquire_cpu`; `THREAD_ENV` 상수 재사용. 원래 scheduler 전체 framework는 실행하지 않는다.

`vendor/resources/bass_resources.py`: BASS commit `106a0153bf113fa4f0beea9743e84a744b65f424`, 원본 resources.py SHA256 `8e46d35d9897ac166000c8f3a5296716fa3cd3c93dc747ca4458e97137f6d60e`. byte 그대로 vendor. `_cpu_counters`만 호출한다. snapshot/process policy 전체는 실행하지 않는다.

`src/shared_runner.py`의 작은 admission/identity-lock/dispatch 코드는 위 helper를 선택적으로 호출하는 이번 pilot용 신규 adaptation이다. cgroup v2 Linux가 필요하다. 순간 busy 관찰은 미래 부하를 보장하지 않는다. registry는 해당 host의 /tmp 수명 동안만 지속하며, 지정된 output root의 완료 결과는 registry 없이도 재사용된다. CPU/RAM 관찰 실패는 추측 실행하지 않고 오류를 반환한다.

## 실행 후 제한된 reserve 교정

최초 28-case 실행의 runner는 RAM reserve에 min(4GiB,total/8)를 사용하여 실제 8GiB sandbox에서 1GiB를 reserve했다. 당시 실행은 최대2worker와 관찰된 실제 가용 RAM 및 job당1GiB budget 안에서 완료했다. frozen contract를 따르도록 이후 max(4GiB,total/8)로 교정했다. 향후 8GiB 할당은4GiB, 128GiB profile은16GiB를 reserve한다. 가용 RAM이 부족하면 capacity만 DEFERRED가 되며 다른 process 존재 자체가 HOLD 사유는 아니다. 이 교정은 과거 실행에 소급 적용하지 않으며 과학 결과를 재실행하지 않았다.
