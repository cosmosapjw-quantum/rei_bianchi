# WU088_HH PHYS53, 다음 실제 코딩 연구 단위: NCP Rust parity

2026-10-16 KST. 이 패키지는 **원격 실행이 도구 월간 한도로 차단된 상태에서** PHYS53의 다음 미완료 작업을 완성할 수 있도록 만든 실행·검증 패키지다. 이전 PHYS53 [PR #92](https://github.com/cosmosapjw-quantum/WU088_HH/pull/92) head `8fe647d4e836204f783e91024f81a3f2c8f46b60` 위에 additive로 게시한다.

## 이번에 실제로 완성한 부분

- 과학 입력 원본: `research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz`, SHA256 `f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d`. GDrive PHYS52 source capsule에서 **실제 21,029바이트**를 복구하여 SHA를 확인했다. 원본을 수정하지 않았다.
- 공식 DLMF 33.8.2의 Coulomb outgoing logarithmic derivative와 33.23의 불안정 영역 주의사항에 근거한 기존 PHYS53 구현을 재사용한다. 원래 비중심 screened H-H Hamiltonian을 중앙 Coulomb surrogate로 바꾼 것이 아니다. **이번 실제 수치 검사는 중앙 Coulomb 기준계에만 한정**한다.
- `scripts/verify_ncp.py`에는 frozen input SHA, 원래 27개 독립 `mpmath` 기준값, finite-double 실수부, depth 768/1152 일치, 1/8-thread 순서·바이트 불변, 12개 동일 출력 benchmark, 오류 명세 및 자원 기록의 실제 검증 코드를 구현했다.
- `scripts/worker_on_ncp.sh`: Rust 1.99의 진짜 native compile/unit-tests, NCP 3개 반경 x 두 depth + 1/8 thread, 21..4096 benchmark를 **최대 8 workers**, `nice +10`, 16 GiB process virtual memory, job당 timeout 180s로 한정한다. 이 셸 스크립트 자체는 `bash -n`만 확인했다. Rust compile/NCP 실행은 **NOT_RUN**.
- `scripts/launch_from_local.sh`: 사용자가 승인한 private-key SSH 경로(`/home/cosmosapjw/.ssh/ncp_key`)를 **복제하거나 출력하지 않고** 사용해 NCP의 새로운 `/root/wu088_hh_phys53_XXXXXXXX`에 소스만 복사하고, 실제 출력/해시/실행시간을 desktop repo로 되돌려 검증하도록 작성했다. 최초 `--preflight-only`를 제공한다.
- `tests/test_verify_ncp.py`: 허위 PASS를 차단하는 정상/결손/원본해시 오염/NaN/worker 불일치/잘못된 benchmark 테스트. 샌드박스에서 원래 `PHYS53` 테스트와 함께 총 **25/25 PASS**. 시험 fixture는 **fake**이고 NCP 결과가 아니다.

## 정확한 다음 실행

로컬 `cosmosapjw` 컴퓨터에서 새 PR branch를 읽은 뒤:

```bash
cd /home/cosmosapjw/chat_research/WU088_HH
git fetch origin research/hh-phys53-ncp-c6-handoff-20261016
git switch --track origin/research/hh-phys53-ncp-c6-handoff-20261016
bash research/hh_phys53_ncp_handoff_20261016/scripts/launch_from_local.sh --preflight-only
bash research/hh_phys53_ncp_handoff_20261016/scripts/launch_from_local.sh
```

여기서 마지막 명령은 실제 NCP 계산을 **동기 실행**하고 데이터를 로컬 작업 트리에 가져온다. 직접 실행할 수 없다면 [CODEX_HANDOFF_PROMPT.md](CODEX_HANDOFF_PROMPT.md)를 Codex에 그대로 주면 된다. 이 작업이 끝나기 전에 결과가 PASS라고 기록하지 말 것.

## 과학 claim gate

(1) 1,386개의 frozen 원본 계수 SHA 동일, (2) 27개 독립 기준 실수부 상대 오차 2e-12 이내, (3) 두 finite CF 깊이의 실수부 일치, (4) 1/8-thread 출력 바이트 일치, (5) `ell=21..4096` 같은 출력에서만 speedup 측정. High-ell `Im Z`는 f64에서 cancellation이 커지므로 acceptance criterion **아님**. 그 양의 전류는 PHYS53 `mp_reference`의 `log10(k/|H|^2)`에서 따로 검증한다.

**도입하지 않는 결과:** infinite angular screened DtN의 coercive uniform inverse, 실제 driven `xi=Fy-phi`, incoming adjoint, H-H `sigma(E)`, Maxwellian `k_HH(T)`, `rei_bianchi HH_R10`. Native subagents NOT_RUN (현재 native dispatch 미노출).

## 로컬 환경·공유 서버

2026-10-16 KST 사용자 제공 SSH key로 성공한 NCP 접속 정보: host `s1a0e5abed09`, nproc=64, RAM=125 GiB, Rust/Cargo 1.99.0 (`. /root/.cargo/env`). 당시 별도 REI Python 작업이 여러 CPU를 사용 중이었다. 기존 작업 중지·프로세스 변경 없이 새 격리 작업경로와 최대 8 thread만 사용하라.

처음 실패했던 bare `ssh root@49.50.142.2`와 달리, 공개키가 반드시 `-i /home/cosmosapjw/.ssh/ncp_key -o IdentitiesOnly=yes`로 선택되어야 한다. 현재 ChatGPT Remote Desktop Commander는 quota 도달로 local/NCP 실행이 차단되었다.
