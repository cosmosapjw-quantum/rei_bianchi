# HE29 → REI cross-repo 최신 intake

## 결론

오늘의 Sigma/Pi pilot에 직접 도움이 되는 재사용물은 C21K의 CPU lease와 output별 중복 실행 방지, BASS의 현재 affinity/quota/load/RAM 관측이다. 독립된 점들을 source와 입력 identity로 고정하여 실행하고, 공통 lease directory를 사용하는 협력 세션끼리 CPU를 나누면 된다. 다른 Codex 프로세스가 존재한다는 사실만으로 중단하지 않는다.

C21K는 CPU lock을 제공하지만 모든 세션의 RAM이나 모든 output root에 걸친 job registry까지 제공하지 않는다. BASS load 관측도 예약 자체는 아니다. 실제 가용자원 관측과 공통 namespace, 같은 과학 job의 identity를 유지해야 한다. 다른 작업을 종료하거나 신호를 보내는 동작은 이 intake에서 전혀 실행하지 않았다.

## 실제 조사 범위

접근 가능한 owner repositories 51개와 terminal page를 확인했다. 이 중 관련 여섯 repo의 branch 이름과 SHA를 matching-refs 및 100개 단위 pagination으로 모두 확보했다. 모든 repo에서 양쪽 branch 집합이 일치했고 빈 terminal page를 확인했다.

| Repository | Branch refs | Pagination | 2026-10-20 이후 PR 수 |
|---|---:|---|---:|
| vigilode | 182 | 100+82+0 | 5 |
| BASS_HE | 86 | 86+0 | 4 |
| bass_cr | 166 | 100+66+0 | 5 |
| WU088_HH | 135 | 100+35+0 | 7 |
| bass | 260 | 100+100+60+0 | 2 |
| rec_bianchi | 132 | 100+32+0 | 5 |

이는 ref inventory의 완결성이다. 모든 branch의 모든 파일을 읽었다는 의미가 아니다. 선택하여 읽은 원문 파일 22개 fetch 기록(동일 scheduler의 두 pin 포함)은 SOURCE_READ_MANIFEST.json에 source URL, Git blob, 실제 읽기 범위, 저장 bytes/SHA와 함께 있다. REI는 별도 agent의 intake와 합쳐야 한다. 다른 대화/백업/미게시 원격 실행의 전역 부재는 주장하지 않는다.

직접 git ls-remote 여섯 건은 browser-proxy:8889 연결 오류로 exit128이었다. 재시도나 우회를 하지 않고 GitHub connector의 실제 결과로 대체했다.

## 재사용할 정확한 source

### C21K scheduler

- Repo: bass_cr, PR89, metadata HEAD dc1c0c0721b74454958e5d16264c24ec465ba1d8.
- 실행 content pin: bab323983dad5206e162dbfdaefc167f2fabea45.
- Path: research/cr_c21k_epoch_cache_campaign_20261021/ncp/scheduler.py.
- Git blob: 01e4a4884bbad3fab7657235c80651196b1d18e0.
- 33596 bytes, SHA256 495f469faf432cba3764781e545d5711b7ba4f652c778b3aaa57589c64f04928.
- content pin에서 실제 다시 읽어 metadata HEAD의 source와 정확히 같음을 확인했다.

CPU lease는 allocation.lease_directory 아래 cpu_<id>.lock에 flock LOCK_EX|LOCK_NB를 잡고 descriptor를 유지한다. 배포에 고정된 global path는 없다. 같은 사용자의 REI/HE29 coordinator가 동일 directory와 파일명을 써야 협력한다.

C21K_OWNER_ALLOCATION_V1은 host fingerprint, expiry, explicit cpu_ids, RSS budgets를 받는다. 현재 affinity와 모든 ancestor cgroup quota/cpuset 및 memory 제한을 반영한다. CPU55를 제외하는 기존 owner 조건, coordinator CPU 한 개, RAM max(1GiB, limit/8) reserve를 유지한다. 작업 수는 worker CPU 수와 (available RAM-reserve-coordinatorRSS)/jobRSS 중 작은 값이다.

중복 identity는 job, source_identity, input_files의 canonical JSON SHA256이다. 같은 output의 CAMPAIGN_IDENTITY, coordinator lock, create-only RESERVATION, payload hash/과학 receipt를 확인하여 정확히 성공한 job을 재사용한다. 다른 output root 사이의 global duplicate registry는 없다.

외부 Codex를 blanket blocker로 삼지 않는다. process cleanup은 자기 attempt token과 startticks를 가진 소유 프로세스만 대상으로 한다. 이 코드를 이 intake에서 실행하거나 process signal을 보내지 않았다.

### BASS resources

- 실제 읽은 immutable ref: 106a0153bf113fa4f0beea9743e84a744b65f424.
- Path: research/bass_isotropy_response_20261018/s12_birth_memory/ncp/resources.py.
- Git blob eff4507bdb8ac5b46e76738de1126a1daf7929e6.
- 14170 bytes, SHA256 8e46d35d9897ac166000c8f3a5296716fa3cd3c93dc747ca4458e97137f6d60e.

snapshot(profile,disk_root,sample_seconds=0.12,own_group_ids=())는 affinity, cgroup CPU/RAM, MemAvailable, perCPU activity, scaled load1, cgroup CPU use, 자기 process groups와 disk를 읽는다. NCP profile 상한64CPU/128GiB에서 현재 제한을 더 적용한다. 외부 load가 있는 경우 남은 자원 판단에 유용하다. 관측을 독점 예약으로 취급하지 않는다.

f4cd0d53760783e6a58c3b0a98c64311ca489d28는 BASS scientific core pin이다. resources.py를 그 pin에서 별도로 읽어 동일성을 확인한 것은 아니므로 helper provenance에는 실제 읽은 106a0153...를 쓴다.

### 정확한 epoch cache 패턴

C21K epoch_adapter.py는 bab323983dad5206e162dbfdaefc167f2fabea45에서 읽었다. Git blob1c82e1098fe16913b55a677cf979f8a90e0e438f, SHA256 fc8009f7e185f7a257cbda0956317f4e7f358a8c548501c96e204aa7c94498bd이다. cell-owned LRU cap16, binary64 exact-byte key, immutable backing, cell reset, 기존 multiplication order를 유지한다. 재사용 가능한 것은 이 의존성 분리 원칙이며 state-dependent RHS 전체를 epoch만으로 캐시하지 않는다.

bass_cr GitHub repository license metadata는 null이었다. 같은 owner 프로젝트 사이의 사용자 지시 재사용으로 출처를 보존하며 임의 SPDX 라이선스를 붙이지 않는다.

## 새 실제 반환과 재실행 제외 목록

| Lane | 실제 관측 | 이번 처리 |
|---|---|---|
| HE29 reference4/pair + canary1 | 부모 intake의 완료 결과 | 재사용, 재실행0 |
| BASS S12 | 새 archive raw GET 성공은 backup agent receipt; 여기서는 추출 SUMMARY/ENSEMBLE/BUILD/manifest를 읽음 | PR174 NOT_RUN은 stale. 원16PASS+case_parallelFAIL, resume16SKIPPED_EXACT_PASS+case_parallelPASS. 17logical job 완료 재사용 |
| REC R3S | Git NCP results/DAG 실제 읽음 | 5job scope 완료. saved audit enum adjudication을 실행 반복으로 세지 않음 |
| REC U4A | Git 결과32steps74411→74443 | scoped pass와 원 CAP_HOLD를 함께 유지 |
| REC U4B | Git 결과32steps74443→74475, 1launch | numerical/restart PASS. whole-allocation CPU/wall UNRESOLVED, REI activation false |
| HH PHYS73 | PR126 사용자 실행 보고 | 15complete+15resume reuse, raw 접근 PENDING. raw를 얻기 위해 같은 job 재실행하지 않음 |
| C21K | 준비 code/manifest/closeout 실제 읽음 | 신규 native0/IVP0. 이 queue를 오늘 REI pilot에 자동 합류시키지 않음 |

BASS S12 새 archive는 157420884 bytes, SHA256 eb522092a7e466d95d87797795fb080583dc0b987555dcaba00ea2fd62813709이다. source f4cd0d..., tree a9048818707ef3f446528631c3b5d6c8171116cc, delivery8247645d..., binary ad74ec3629afc0934a297ea4fa5159f681f254b20431d704a1fb5cb38b4d794e를 식별했다. 고정 k16/n64의 제조 history14개(11full+3omission), checks30/30 결과이다. continuum/full spectral 인증으로 확대하지 않는다. raw-byte 검증의 실행 주체와 상세는 backup_context_intake의 영수증을 인용한다.

REC U4B execution source a09e1d249d4cf4b706c09571fa7f231c8084c251, checkpoint SHA1a8a224ff473c2c2cd054bc6ec78bcb06ee900b9e2694a9f30509591a56b5446이다. common-input128, max scaled RHS1.3991210612405974e-13, native checkpoint restart maxstate4.930470639159558e-14, split16+16과32의 saved output exact equality가 기록됐다. 이 stored result를 읽었으며 해당 과학 계산을 다시 수행하지 않았다.

## 최신 VigilODE 경계

PR77만 읽으면 놓치는 production/vigilode-plan-20261021 branch가 있다. HEAD cc2e1a009ac6802ef01a289392e9715074a882ba, tree ce612bf7dc46c5790ee698c167ada46c41422a0a에서 WAVE3_REPORT와 OPEN_ITEMS를 읽었다. fast dense/banded의 component atol, dense output/controller, events 경로가 추가되어 있다.

B1c lagged-factor staleness killgate는 FAIL이며 driver가 기본 경로에 연결되지 않았다. E1b workstation walltime은 high load 때문에 INCONCLUSIVE/diagnostic_only다. dense local estimate는 global error certificate가 아니다. 따라서 오늘 source-frozen CanonicalFV pilot에 새 solver migration을 요구하거나 HE29에서 미측정 speedup을 주장할 이유가 없다.

## 단계 마감

- DAG: R2/C2 bounded intake COMPLETE.
- 재사용 결과와 이번 read-only 관측을 분리했다.
- 새 science/test/benchmark/native/NCP submission/process signal/remote mutation: 모두0.
- 로컬 증거 저장 완료; Git 게시와 백업은 부모 통합 단계가 담당하며 이 agent는 수행하지 않았다.
- 적용 skill은 standalone1.0.0 RESEARCH_POLICY/EVIDENCE_AND_HANDOFF와 plugin1.3.0 POLICY_INTEGRATION이다. 버전 전환을 이유로 완료 연구를 반복하지 않았다.
