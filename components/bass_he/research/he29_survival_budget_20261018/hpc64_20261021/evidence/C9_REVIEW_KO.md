# HE29 HPC64 C9 독립 검토

## 판정

**PASS_SCOPED_AFTER_ONE_CLOSED_FINDING**. 단일 독립 검토에서 실행 호환성 finding 한 건을 발견했고, 작성자의 최소 수정과 해당 표적 검증을 읽어 종결했다. 미해결 blocking finding은0건이다. 이 판정은 검토한 코드와 이론 주장의 범위에 대한 것이며, NCP 실행·실제 속도·Git 게시·백업 완료를 뜻하지 않는다.

검토자는 앞선 Git intake만 담당했으며 새 구현과 테스트를 작성하지 않았다. physmath-research-loop1.3.0 C9를 한 번 수행했고, R6의 이론 타당성·주장 범위와 R9의 수학식–구현 연결도 같은 검토 단위에서 읽었다. 하위 reviewer나 새 검토 루프를 만들지 않았다. 검토한 실제 파일의 SHA256과 증거 목록은 `C9_REVIEW.json`에 있다.

## 발견과 수정

**C9-F1 — cgroup v2 실제 최상위 그룹을 관측 실패로 처리.** 처음 구현은 모든 ancestor에서 `cpu.max`와 `memory.max`를 요구했다. Linux의 실제 최상위 그룹은 해당 resource-control 파일을 갖지 않으므로 정상 호스트에서도 실행 전 HOLD가 발생할 수 있었다. 과학적 false PASS는 발생시키지 않는 실행 준비 결함이었다.

[Linux 공식 cgroup v2 문서](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)는 최상위 그룹의 예외와 세 non-root 인터페이스를 명시한다. [Linux v6.8의 실제 소스](https://github.com/torvalds/linux/blob/v6.8/kernel/cgroup/cgroup.c), Git blob `a66c088c851cfb87036ccc93317f7357769cb268`도 읽었다. `cgroup.type`의 제외 판정은 실제 parent 존재에 근거하므로 namespace 안에서 경로가 `/`로 보이는 사실만으로 최상위 그룹이라고 인정하지 않는다.

작성자는 읽힌 `cgroup.controllers`와 `cgroup.type/cpu.max/memory.max`의 명시적 NOT_FOUND를 결합한 actual-root signature만 허용했다. 하위 그룹의 quota와 memory headroom은 계속 적용하고, namespace root·permission denied·근거 부족은 HOLD한다. 수정된 `host_plan.py` SHA는 `1431bcc581f1fac40d3f6d2ad03a4925d9e8de0985b00639f19a0b55059b79bc`다. 새 표적4 method 첫 PASS의 실제 receipt/stderr와 코드를 읽어 종결했다. 기존 host12 method는 다시 돌리지 않았다.

작성자가 별도로 찾은 상대 argv의 cwd namespace 누락 수정도 읽었다. 새 표적2 method 첫 PASS이고, 이 수정은 독립 C9 finding 수에 중복 합산하지 않는다.

## 확인한 수치와 실행 계약

- **테이블:** 원래 `ExactSource.source_moments`의 행 내부 산술을 유지한다. 서로 독립적인 worker 모델과 고정 `(interval,row)` 위치로 조립하며 전체 canonical digest와 마지막 canonical diagnostics를 복원한다. 원래 NCP runtime의 전체 `919ca6…` table SHA가 맞아야 solver에 진입한다.
- **캐시:** exact source/runtime/thread/spec/grid identity를 key로 쓴다. create-only 파일, 크기/SHA/dtype/shape/finite·positivity 및 원래 table digest를 검증하고 read-only mmap을 사용한다. incomplete cache는 보존하고 HIT의 build telemetry를 새 실행으로 세지 않는다.
- **과학 계산:** a5의 원래 solve/check_result/admit_pair와 네 baseline pair gate를 재사용한다. thread1,19-ledger full-state norm, 허용치·source/binary/input/runtime cohort를 유지한다. production 경로에 RNG나 인공적인 물리 seed는 추가하지 않았다. 제조 I/O payload의 고정 정수 생성기는 재현 가능한 비물리 문자열 fixture다.
- **기록:** B256은 기존 per-call 내구성과 다른 계약이다. 성공 point 반환 경계에서 마지막 완료 fsync 이후 최대255개가 미동기화일 수 있다. segment/failure/RAW/close barrier, sticky I/O 실패, 완결 gzip readback 및 written/durable/verified/calls 일치가 최종 RESULT 앞에 연결돼 있다.
- **제어:** 새 subprocess와 worker는 검증된 ed5 whole-group watchdog을 재사용한다. shared stable flock, 실제 `/proc`와 cwd 관측, bounded saved-output intake, dispatch 직전 재관측이 한 canary 전에 연결돼 있다. 다른 실행을 종료하거나 기존 부분 결과를 덮어쓰지 않는다. local scope를 전체 원격 실행의 부재로 일반화하지 않는다.
- **자원:** table48/build8은 상한이고 두 phase는 순차 실행이다. 실제 affinity/quota/memory headroom과 reserve,CPU55 보호를 적용한다. memory estimate를 측정된 전체 RSS 상한으로 주장하지 않는다. Cargo CLI와 환경변수 및 build receipt의 job 수가 일치한다.
- **진입·반환:** publication DELIVERY에서 code pin을 읽은 뒤 분리된 clean checkout으로 실행한다. a5/ed5/source pin과 문서 HEAD를 구분하고 기존 DATA·binary·runtime·기준해를 재사용한다. 반환 archive는 실제 payload readback을 하며 provider upload나 과학적 admission을 자동으로 주장하지 않는다.

## 이론·성능 주장 경계

행 순서 보존은 같은 입력/runtime/source에서 같은 행 bytes가 생성된다는 조건부 논증이며, 작은 subset 확인이 전체 table 검증을 대신하지 않는다. 기존 r4/table512 두-method pair의 table 비율3.7922%와 table-only Amdahl 상한1.03941698은 그 과거 pair에 한정된다. 제조 I/O3.24186배는 해당 filesystem/workload의 결과다. 실제 HE29·NCP64 속도나 다른 배율과의 곱으로 표현하지 않았다.

RNG 없는 production 코드와 제조 trace의 고정 payload 생성, source-row subset과 전체 golden table, gzip semantic record identity와 압축 archive byte identity, source pin과 publication 문서 HEAD가 구분돼 있다. 두 solver의 일치를 참 ODE 해의 오차반경으로 해석하지 않는다. 연속 스펙트럼·전역 gas-temperature·전체 EoR·upstream 전체 동등성·Bianchi/CMB HOLD는 유지한다.

## 증거 재사용과 남은 실행

새 초기 method 수는 table11+trace11+canary10+host12+batch/build12=56이다. 서로 다른 새 cwd2와 root4를 더한 **고유 method62개**의 첫 실행 결과를 읽었다. source-row256×640 subset 한 번, 제조 I/O9 sample, shell syntax2개와 제조 반환 package/readback 한 번은 별도 근거다. 검토자가 테스트나 기존 campaign을 다시 실행한 횟수는0이다.

기존 a5/ed5/09929와 원래 과학·transport·tests·benchmark/clean-build 증거를 재사용했다. actual NCP 제출0/시작0, 원격 프로세스 UNOBSERVED, packed canary NOT_RUN, 실제 HE29 속도 미측정이다. 접근 가능한 실행자가 원래 runtime과 전체 table hash를 확인한 후 준비된 단일 canary를 실행해야 한다.

최신 README/DAG/DELIVERY의62개 검사·기준해4/4 재사용·실행0과 게시/보존 상태를 실제 읽었다. Intake 게시 `cbbed9c3da6b41914527e322d2cb9bea9dc7b1f3`의8개 readback, stage1 Dropbox payload9/member10 PASS와 Drive bounded receipt 대기 상태가 기록돼 있다. 새 code_commit은 아직 null/readback PENDING이며 R10/C10도 게시·보존 진행 중이다. 공식 stage guide에 따른 단계 이름/근거 매핑 수정은 재계산 없이 parent가 반영한다. 최종 code pin과 readback, 문서 HEAD 및 후속 백업 상태는 실제 영수증으로 채워야 한다. 이 C9 판정 자체로 게시나 백업을 완료 처리하지 않는다. Parent는 검토한 source bytes를 게시하고 실제 code pin을 고정한 뒤 보존·인계를 마감할 수 있다.
