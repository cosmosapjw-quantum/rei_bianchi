# HE29 native evidence batching: 채택 범위

## 변경과 보존

`BatchedNativeOwner`는 SHA256
`a72767ac013fe1cfe6d4d96a335e6b3d1194ec34c3e6baa3887f5babd0aa6d9e`인
원래 `he25_proper_birth_20261016/src/native.py`를 읽어 상속한다.
`point`, `density`, stdin request framing, 응답 parsing, source handshake,
binary digest 및 원래 물리 입력/출력 검증은 변경하지 않는다.
Native source는 `f7830e2f55e7a1938bc3c98f61b60651f8dae474`이고,
실제 NCP runner는 원래 admission의 binary `a82e5407…`와 expected SHA를
연결해야 한다. 이 제조 시험은 해당 HE29 binary를 실행하지 않았다.

변경은 gzip JSONL evidence의 동기화 시점이다. 모든 원래 event와 모든
request/response 문자열을 순서대로 기록한다. B=`sync_every` 기본값은
256이며, B=1은 원래 point마다 flush/fsync하는 스케줄이다. Handshake,
failure, close_failure는 즉시 동기화한다. 정상/통상 실패 close는 남은
모든 기록을 동기화하고 gzip trailer를 닫아 fsync한다. 전체 gzip을 끝까지
읽고 JSON record 수와 source/binary identity를 확인한 뒤 정상 세션만
create-only link로 최종 파일을 게시한다. 실패 세션은 `.partial`을 남긴다.
경쟁 final 파일은 덮어쓰지 않는다.

## 내구성 계약과 증명 범위

마지막 완료 fsync 이후 point record 수를 p라고 하자. 새 point record를
기록한 뒤 p>=B이면 해당 point 호출이 반환하기 전에 fsync를 수행한다.
따라서 성공한 point 반환 경계에서는 0<=p<=B−1이다. Handshake/failure와
명시적 checkpoint barrier는 p를0으로 만든다. 동기화가 실패하면 그 point
호출 또는 checkpoint가 예외를 전파하고 owner를 failed로 고정한다.

이것은 process hard kill 때 마지막 fsync 뒤에 있을 수 있는 **성공 반환한
point 기록 수**의 상한이다. B=256은 최대255개 point 기록의 미동기화
구간을 허용한다. 원래 per-call durability와 같다고 주장하지 않는다.
커널/파일시스템/전원 장애에 대한 절대 보장도 아니다. 강제 종료된 gzip
partial은 trailer가 없을 수 있으며 정상 final과 동일한 gzip 완결성을
가정하지 않는다. 과학 RESULT admission에는 완결된 gzip 전체 readback을
요구한다.

Parent는 각 segment checkpoint와 RESULT admission 전에
`owner.flush_evidence(reason)`을 호출한다. `with` 종료 뒤
`owner.evidence_telemetry()`에서 complete_gzip_readback,
written/durable/verified count 일치, trace_error=None, owner_failed=False를
확인해야 한다. fsync 오류는 나중에 close가 바이트를 보존했더라도 sticky
failure로 남는다. 디렉터리 fsync 실패가 최종 link 뒤에 발생하면 생성된
파일을 보존하지만 호출은 실패하고 과학 RESULT를 admit할 수 없다.

## 실제 새 검증

`TRACE_TESTS_FIRST.json`: 2026-10-20 20:50:26 UTC에 새11 method 첫 실행
PASS. 실제 제조 stdio process를 사용하여 B=1/3/256의 모든 point 출력
binary64 bytes와 모든 request/response record의 semantic identity를
원본에 대조했다. Monotonic timestamp만 비교에서 제외했으며 gzip 압축
bytes identity는 주장하지 않았다. Batch boundary/segment barrier,
ERROR/EOF partial, source/input 검증, final/partial/symlink overwrite,
publication race, startup/point/checkpoint/directory fsync 실패, corrupt
gzip의 publication 차단을 포함한다. 기존 테스트와 과학 계산 재실행0.

`TRACE_PROBE_FIRST.json`: 같은 filesystem에서 제조 point4096개,
3개 정책(original/B1/B256), 3회 회전 순서 측정. 실제 gzip/flush/fsync/
close/전체 JSONL readback을 시간에 포함했다. Original에는 비교를 위해
완결 readback을 추가했으며 B256은 새 close의 자체 readback을 사용했다.
별도 semantic SHA 검사에서9개 trace의 모든 event가 timestamp를 제외하고
일치했다. 실제 fsync calls는 sample마다 original4099, B1=4100, B256=20.

중앙 wall time은 original1.977382622s, B1=2.009101999996s,
B256=0.609952585s. Original/B256=3.241862844배, B1/B256=3.293865867배다.
이는 이 제조 I/O workload의 실측이다. 실행 환경은 affinity9 CPU,
cgroup CPU quota8 core 상당, memory8GiB이며 **NCP64가 아니다**.
HE29 전체 solver 가속률은 아직 측정하지 않았다. 과거 CSR/IVP 가속률이나
64core 개수와 이 비율을 곱하지 않는다.

## 종료 상태

Evidence batching 구현과 변경 범위의 경량 검증은 완료했다. 기존 native
physics/solver/reference 검증을 재실행하지 않았다. Parent runner의 barrier
연결, 실행 source/환경 cohort 및 실제 NCP 결과는 별도 통합/실행 범위다.
