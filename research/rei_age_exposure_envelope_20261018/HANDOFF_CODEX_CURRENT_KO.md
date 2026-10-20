# Codex/NCP 현재 인계 | v10 time8·16·32 한 캠페인

Repo `cosmosapjw-quantum/rei_bianchi`, draft PR199, branch `research/rei-age-exposure-envelope-20261018`, task `research/rei_age_exposure_envelope_20261018/`.

## 목표와 먼저 확인할 상태

이번 연구에서 N2/N3/N4를 원 count/energy gate로 복구하는 제한된 subnormal support 변경, order-preserving cohort parallelism, compact observation trace, accepted chemistry의 저장 분모 BE observer를 구현·컴파일·작게 검증했다. 최종 R6/C9 및 publication/backup receipts를 읽는다. NCP에는 컴파일·작은 환경 연결·실제 time8/16/32 실행만 남긴다. 완료 age32·age64·spectral128·v7 benchmark·v8 fixed-model은 반복하지 않는다.

최신 PR199 HEAD와 CURRENT5 및 이 배송 이후 새 결과를 먼저 확인한다. 완료 matching case는 raw/receipt를 읽어 ingest한다. 실패·중단 attempt를 새 directory로 옮겨 budget을 초기화하지 않는다. Native age/time 수렴 HOLD, nonlinear Grackle response bound NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED는 exit0만으로 바뀌지 않는다.

## 자동 복원과 환경 연결

1. 기존 owner checkout의 branch/HEAD·dirty/untracked·진행 중인 작업을 확인하고 보존한다. 별도 clone/worktree를 만들지 않는다. Task-owned source/runtime/output만 변경하며 PR150/R9·LRS·별도 BASS HHeD를 변경하거나 중단하지 않는다. Prepared/build target은 이번 source identity의 별도 task-owned 경로를 쓴다.
2. Git source가 없으면 connector 또는 이미 설정된 rclone으로 CURRENT receipt의 v10 C10을 자동 내려받아 whole SHA/size를 확인한다. C10 task source에 별도 v10 confirmation exact UTF-8 delta를 적용해 최종 task tree를 복원한다. `archive_only/RESTORATION_LAYOUT.md`와 confirmation의 exact file set을 따른다. User에게 ZIP 이동·해제를 요구하지 않는다.
3. Frozen native153와 stored native32는 `campaign.py --c10`이 자동 복원한다. C10에는 native153/B1/source161/vendor22·865와 native32 원 tar가 있다. V9 C10도 같은 immutable native inputs fallback이다: SHA `5eef15a565636fa1e7c160aa30f3b2bb294dfa00364e504ee774f867c6ca4995`,bytes25,147,021,Drive `1c6bCjR8oY3bhr337zqjVOi03lUbIclwD`,Dropbox `id:BSpOijBcT10AAAAAAD_aAA`. 실행 source는 최신 v10을 쓴다.
4. 실제 host affinity/cgroup CPU quota/current memory headroom·현재 jobs를 확인한다. 이번 대화의 device list는 성공했지만 config 조회는 현재 월 Desktop Commander usage cap이었다. 재시도/재접속하지 않았고 실제64/128 host·기존 jobs는 NOT_OBSERVED, 새 NCP 제출0이었다. 다음 환경의 정상적인 가용 실행 경로를 확인한다.
5. 기존 NCP venv의 Python3.12.3/NumPy2.3.5/SciPy1.17.0을 우선 사용하고 실제 runtime을 기록한다. Sandbox Py3.12.14와 동일하다고 쓰지 않는다. 실제 rustc/cargo 위치를 찾아 bin의 부모를 `--rust-prefix`에 넣는다. 새 전역 설치가 아니라 필요한 기존 runtime 연결을 한다. Native crate는 offline build한다.

## 한 명령으로 남은 case 모두 실행

아래 변수는 Codex가 기존 경로·최신 source·자동 확보 archive를 찾아 직접 설정한다. User가 경로를 찾거나 파일을 준비할 필요가 없다. REI_TASK=repo task절대경로, REI_PY=기존 compatible Python, REI_RUST_PREFIX=Rust bin부모, REI_C10=자동확보 archive, REI_RUNTIME/REI_RUN=이번 source/attempt의 task-owned 경로다. 기존 결과를 보존한다.

~~~bash
"$REI_PY" "$REI_TASK/native_optimization_20261021/campaign.py" \
  --runtime "$REI_RUNTIME" --out "$REI_RUN" \
  --c10 "$REI_C10" --rust-prefix "$REI_RUST_PREFIX" --plan-only

"$REI_PY" "$REI_TASK/native_optimization_20261021/campaign.py" \
  --runtime "$REI_RUNTIME" --out "$REI_RUN" \
  --c10 "$REI_C10" --rust-prefix "$REI_RUST_PREFIX"
~~~

Shared host에서는 `--available-cpus`와 `--available-memory-gib`에 이 task에 실제 배정 가능한 양을 명시한다. 다른 job의 자원을 가용으로 간주하지 않는다. Verified idle64core128GB 기본값은3cases×20workers+3main=63slots,BLAS/OMP1이다. `--repo`는 original Git objects가 이미 있는 offline 대안이다. Stored age32 자동 비교까지 연결하는 `--c10`을 권장하며 두 옵션을 동시에 주지 않는다.

| 항목 | 동결 값 |
|---|---|
| Original native | `35d9747a0bbedcafdb568467ce7c1e7a25f965b6` /153files |
| Positive B1 reference SHA256 | `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4` |
| Computational base SHA256 | `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620` |
| Cases | time8,time16,time32 각1회 |
| 공통 설정 | q0/birth32/n_mu8/source8/transport16/common8·16·32·64 |
| 수치 경로 | 원 native BE/Newton, opt-in subnormal-barycenter, 원 count/energy/Newton gates |
| Observer | accepted chemistry STORED_DENOMINATOR_DISCRETE_BE streaming ON |
| 큰 host 기본 자원 | jobs3/workers20/63slots/case address space24GiB/reserve16GiB |
| 각 case wall |1800s |
| Aggregate child wall |5400s,기존 attempts 포함 |
| Campaign elapsed | jobs3→2000s,jobs2→3800s,jobs1→5600s |
| Build | 별도300s |
| 작은 preflight | 각 control30s,persistent light cap240s |
| 자동 재시도 |0 |

B1은 원 positive reference binary다. 새 BE binary는 generated source/compiler/runtime과 별도 SHA로 기록하고 B1과 byte-identical이라고 쓰지 않는다. Campaign은 source/prepared/binary/runtime/host/argv/env를 연결하며 stale prepared/build를 재사용하지 않는다. 작은 compiled preflight 뒤 세 heavy case를 실행한다. 유효한 tiny domain2birth/n_mu8/source8/transport8만 쓰고 원 guard를 완화하지 않는다.

## 반환·분석·게시

Stdout/stderr, RECEIPT, HOST, CAMPAIGN, argv/env/source/prepared/binary/runtime, output SHA, repair counters, accepted BE trace를 모두 보존한다. Timeout/실패 prefix를 지우지 않는다. Controller interruption에는 살아 있는 자기 child를 확인해 중복 launch를 막고 wall debit을 유지한다. 다른 lane process를 종료하지 않는다.

완료 case에는 원 validate_outputs를 적용한다. 자동 분석은 time8↔16,time16↔32,각 case↔저장 age32를 원0.005 목표와 함께 기록한다. Age32는 positive DOP853, time cases는 native BE이므로 cross-operator 비교임을 명시한다. 빠진 case는 MISSING, 실패 prefix는 INCOMPLETE다. Identity/hash 검증에서 거부된 결과를 postprocess에서 다시 성공으로 사용하지 않는다. Stored denominator enclosure를 continuous-path/Grackle response certificate로 확대하지 않는다.

세 case 종료 후 원 실패가 남으면 첫 새 실패를 진단한다. 동일 자동 반복·허용오차 완화·완료 campaign 반복은 없다. 작은 연결 수정에는 이유/source diff/binary identity를 남기고 모델·solver 변경은 원 연구 계약으로 돌아간다.

반환을 task-owned evidence에 보존하고 실제 최신 원격 부모를 잇는 expected-head FF로 push한다. 결과 archive와 필요한 source C8/C10을 Drive `rei_bianchi_research_backups` 및 Dropbox `/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`에 자동 백업하고 whole readback한다. CURRENT5/DAG에 case별 COMPLETE/FAILED/INCOMPLETE·남은 분석을 반영한다. PR199 draft/open,no merge/no force-push. Root CI와 scoped 연구 검증을 구분한다.


## v10 실제 소스·이중 백업 전달 — 20261021

소스 `4f13648985e417028c530892ea02be4f56018a31`을 부모 `abbf71caf4bd45af5bdf8bc7744690d10b8715e7`에서 expected-head fast-forward로 게시했다. 소스 root tree는 `7314041a7b58d35df4a4b417dcdcfcd34d9f5b15`, task tree는 `1107a5039615148ff72f6fb68d8b72dfce157012`이며 전체 task 소스는2391파일이다. PR199는 open/draft 상태다.

| 패키지 | bytes | SHA256 | Drive ID | Dropbox ID |
|---|---:|---|---|---|
| C8 | 23546319 | `c55dc1280a8fc0154e7fc577e0aab9b2d14853c721b80e620972a4a7bb7b9bdd` | `1n0xltg0nngOih7FVuhuGoI6LoeaC5UbS` | `id:BSpOijBcT10AAAAAAD_aPw` |
| C10 | 25611513 | `d6f2c121f554d3e59d56a15abe910a6dba115a69b167539de42b0df7eb5fd6c5` | `1d80Dn9O92FocYbojvFyF7Qewb2yt5w9-` | `id:BSpOijBcT10AAAAAAD_aQA` |

네 원격 파일을 실제 전체 다운로드하여 bytes/SHA256, ZIP CRC, 전체 payload, 소스 blob/mode/task tree를 확인했다. C10은 frozen native153, 원 B1, deduplicated source161, vendor22패키지/865파일, 원 native32 tar까지 통과했다. 영수증은 `evidence/delivery_v10_20261021/`의 여섯 delivery JSON이며, 전체 원격 검증 상태는 `PASS_FOUR_FULL_PROVIDER_READBACKS`다. 비공개 단일사용 download URL은 게시하지 않는다.

실제 소스 CI는 PR run39509350736/job118926184408 및 push run39509344439/job118926162607에서 기존 root `cargo fmt` 실패, workspace tests SKIPPED다. 전체 PR CI가 green이라는 주장은 하지 않는다. task R6/C9의 scoped PASS와 구분한다.

C8/C10은 위 소스 snapshot을 고정한다. 최종 delivery metadata commit과 실제 readback 이후, 외부 `REI_AGE_ENVELOPE_DELIVERY_CONFIRMATION_20261021_v10.json`에 정확한 task 소유 UTF-8 delta를 넣어 최종 tree를 복원한다. 확인서 자신의 SHA/provider 수신확인은 외부에 둔다. 아직 확정되지 않은 final head/hash를 이 metadata에 쓰지 않는다.

미완료 time8/time16/time32 실행은 `READY_EXPLORATORY_NCP`다. 이번 NCP 새 실행은0이며 native age/time convergence는 HOLD, nonlinear response bound는 NOT_ESTABLISHED, production scientific admission은 NOT_ISSUED를 유지한다. 원격 백업의 완료는 실제 time endpoint나 수렴 판정의 완료를 뜻하지 않는다.
