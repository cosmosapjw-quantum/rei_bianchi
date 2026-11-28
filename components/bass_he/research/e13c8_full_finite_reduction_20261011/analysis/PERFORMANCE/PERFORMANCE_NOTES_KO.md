# E13C8 실제 병렬 실행 성능 분석

## 결론

2,331개 OFF 경로의 N1024/P60 계산은 64개 MPI rank에서 실제로 완료되었다. 전체 controller wall은 **33.963755분**, MPI launcher wall은 **33.237507분**이다. 64개 rank 전부 과학 경로를 계산했으며 각 rank가 CPU 0–63 중 하나에 고정되었다. MPI rank 하나를 controller 전용으로 비워 두지 않았다. [원자료: `BATCH/EXECUTION_RECEIPT.json`, `BATCH/LAUNCH_PROCESS_RECEIPT.json`, `BATCH/ranks/rank_*/START.json`, `BATCH/ranks/rank_*/RECEIPT.json`]

## 실제 관측과 계산한 비율

| 항목 | 실제 결과 |
|---|---:|
| 새 경로 / 계수 평가 | 2,331 / 9,547,776 |
| rank당 경로 수 | 36–37 |
| rank wall 최솟값 / 최댓값 | 1922.839904 / 1993.429486 s |
| rank wall 평균 / 최댓값 | 98.439877% |
| 모든 경로의 보고된 wall 합계 | 125305.302990 s (34.807029 h) |
| 예약부터 완료 검증까지의 동시 경로 수 평균 | 62.981196 |
| 64개 경로 예약 구간이 겹친 시간 | 1901.130558 s |
| controller에서 launcher 밖에 쓴 시간 | 43.574874 s |

각 경로의 wall 합계는 **동일 작업의 직렬 실행시간이 아니다**. 경로 실행 중의 대기·스케줄링·I/O·64-rank 환경의 경쟁이 포함된다. UTC 예약→검증 완료 구간이 겹쳤다는 사실 역시 CPU가 실제로 바빴다는 샘플이 아니다. 저장된 runtime은 `perf_counter`와 `ru_maxrss`를 기록하며, user/system CPU-time이나 `cpu.stat` 변화량을 기록하지 않았다. 따라서 **CPU 이용률과 같은 작업의 직렬 대비 speedup은 NOT_MEASURED/NOT_ESTABLISHED**다. [원자료: 잠긴 `code/off_path_worker.py`, `code/parallel_batch.py`; 직접 계산: `PERFORMANCE_ANALYSIS.json`]

## 부하 분산과 예측 오차

rank wall의 최대−최소 차이는 70.589583 s다. 실제 관측된 각 경로의 시간을 고정해 다시 분배하는 사후 산술 LPT 모형에서는 가장 긴 shard의 경로시간 합계가 1989.163331 s에서 1972.945512 s로 줄어든다. 가능한 차이 16.217819 s는 실제 controller wall의 0.795840%다. 이 값은 실행한 새 scheduler의 성능이 아니라, 경로시간이 재배치 후에도 같다고 가정한 사후 계산이다. 현재 자료는 동적 scheduler로 전면 교체할 큰 이득을 보여 주지 않는다. [원자료 및 계산: `PERFORMANCE_ANALYSIS.json#/balance`, `#/per_rank`, `#/per_path`]

기존 N1024 예측은 이상적인 64-rank 24.966078분, 가정한 80% 시나리오 31.207598분, 50% 시나리오 49.932157분이었다. 실제 33.963755분은 80% 시나리오보다 8.831688% 길며, 두 시나리오 사이에 있다. 이것은 **예측 오차 비교**이며 측정한 병렬 효율로 이름 붙이지 않는다. 각 종 수별 실제 64-rank 경로시간 평균은 JSON에 별도로 보존했다. [원자료: E13C7 `analysis/RESOURCE_ALLOCATION.json`; 실제 실행 영수증]

## 메모리

rank별 lifetime 최대 RSS 중 가장 큰 값은 59500 KiB이다. 64개 rank 각각의 최대 RSS를 합하면 **3.590969 GiB**, controller의 개별 최대 RSS까지 합하면 **3.657955 GiB**다. 이 합은 시점이 서로 다른 최대값의 합이며, 공유 페이지 중복 집계 가능성이 있고 MPI daemon·wrapper·page cache·다른 프로세스는 포함하지 않는다. 따라서 실제 동시 전체 메모리 peak로 표기할 수 없다. 경로별 `ru_maxrss`는 같은 rank 프로세스의 누적 최대값이므로 2,331개 값을 합하면 잘못된 수치가 된다. [원자료: rank 및 controller receipt; 메서드: 잠긴 runtime의 `resource.getrusage(RUSAGE_SELF).ru_maxrss`]

이번 작업은 메모리 용량이 주된 병목이라는 증거가 없다. 128 GB를 채우려는 계산은 추가하지 않는다. 64개 계산 rank와 작고 균형 잡힌 tail을 사용한 이번 중량 실행을 마친 뒤, 다음 과학적 판단과 경량 합산을 여기서 처리하는 것이 사용자 정책에 맞는다. 새로 필요한 중량 작업이 생기면 이번 실제 시간 분포로 계획하고, 그 작업에 저비용 CPU-time 관측을 함께 기록하면 된다. 이미 끝난 경로를 성능 측정만을 위해 반복할 이유는 없다.

## 재현 범위

이 분석은 실제 저장한 JSON만 읽었다. 과학 커널 호출, MPI 실행, benchmark replay는 모두 **0**이다. 입력 identity와 64개 rank 및 2,331개 경로의 연결을 검사하고, UTC 겹침의 sweep 합계가 각 구간 길이의 직접 합과 일치함을 확인했다. 비율의 exact 필드는 관측 파일에 기록된 십진 시간값의 정확한 비율이며 물리적 시간 측정의 무한 정밀도를 뜻하지 않는다. Provider attestation은 **NOT_ASSERTED**다. 입력 pin과 재현 명령은 `PERFORMANCE_ANALYSIS.json#/provenance`와 `#/analysis_execution`에 있다.
