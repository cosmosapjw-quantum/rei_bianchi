# HE32: 2026-10-22 저장 결과 복원 완료

이 문서는 완료된 HE32 연구 단원의 실행 공간 유실 후 **파일 복원**을 기록한다.
원래 과학 작업 O.C1–10 → P.R1–10 → F.C1–10은 30/30 완료 상태다.
이번 재개에서는 새 IVP, benchmark, 그림 재생성, NCP job을 실행하지 않았다.

## 확인한 완료 상태

- 원격 PR85는 open draft이고 이번 복원 시작 HEAD는 `88f9957d219f71b458b3bcaf41ccdde60538379f`였다.
- Python 3.12.14 / NumPy 2.3.5 / SciPy 1.17.0 / Matplotlib 3.10.8이 기존 실행과 같다.
- 전체 archive 74,510,381 bytes를 실제 GET 1회로 복원했다.
- 1,392 payload의 SHA256, 크기, mode, 안전하고 중복 없는 경로 집합이 모두 일치한다.
- `results/` 810개와 단계 archive 30개를 별도 복원 경로에 추출했다.
- Git의 source/data/vendor 16개 및 기존 tracked results 15개가 archive와 일치한다.
- 394 NPZ + 대응 case JSON 394개, PNG/SVG 6쌍, 30개 단계 archive가 있다.
- `valid_render` 사전 확인 후 `run.sh plot --out`은 exit 0 / `REUSED_COMPLETE_RENDER`를 반환했다.
- 결과 파일 전체의 bytes/SHA256/mtime/경로 집합이 호출 전후 같다.

이번 archive는 이전에 완료·게시된 artifact-loss recovery campaign의 파일을
그대로 복원한 것이다. 과거 원 실행 394 + artifact-loss recovery 394라는 실행
이력은 그대로 유지하며, 이번 파일 복원의 과학 IVP는 0이다.

근거: [완료 영수증](RESUME_RESTORED_20261022.json),
[전체 백업 검증](ARCHIVE_RESTORATION.json),
[선택적 추출](SELECTIVE_RESTORATION.json),
[저장 그림 재사용](SAVED_RENDER_REUSE.json).
초기 환경 오류와 복원 전 상태는 `RECOVERY_INVENTORY.json`에 보존했다.

## 실제 경로와 열람 명령

```bash
HE32_CODE=/tmp/he32_resume_20261022/repos/BASS_HE/research/he32_sandbox_primordial_20261021
HE32_RESULTS=/tmp/he32_resume_20261022/restored/research/he32_sandbox_primordial_20261021/results
bash "$HE32_CODE/run.sh" plot --out "$HE32_RESULTS"
```

기존 그림은 `$HE32_RESULTS/figures/`에 있다. 현재 결과는 복원된 원자료이므로
`run`이나 `--recover-missing-artifacts`를 호출할 필요가 없다.
Git의 최신 문서와 ACK는 유지했고, 전체 archive의 오래된 문서로 덮어쓰지 않았다.
다른 환경에서는 README의 SHA 검증과 별도 디렉터리 추출 절차를 사용한다.

전체 archive:
`BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz`

```text
SHA256 27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a
Dropbox ID id:BSpOijBcT10AAAAAAD_hsw
Dropbox revision 65e60f6443d950af03d47
executor SHA256 99f4a0e248d853d641393d78bcc330c4b3913ad1da1b326219e3fa3f60375314
```

## 적용 범위

이번 복원은 기존 조사 이후 HE32 branch와 해당 archive의 변경 여부를 확인했다.
모든 repo/branch의 신규 전수 독해나 다른 대화 원문 회수를 했다는 뜻은 아니다.
상세 선행 조사 범위는 단원 `RESULTS_KO.md`와 `evidence/intake/`에 있다.

현재 물리 모델은 n,H1,D,T,He3,He4,Li6,Li7의 21개 중성/양이온 상태를
기록하고, 같은 원소 동위원소의 공통 electronic rate 가정을 사용한다.
matter stress는 nonbaryonic collisionless sector이며 원자 기체에는 pi_b=0
closure를 적용한다. 광자와 중성미자 stress는 부호를 합친 뒤 norm을 취한다.
모든 불안정 isotope, 음이온, 분자, fully reactive 19채널 핵반응망이나
바리온의 kinetic anisotropic stress까지 완료했다고 해석하지 않는다.

## Codex handoff — 복사 가능

```text
HE32의 완료된 pilot을 사용한다.
repo cosmosapjw-quantum/BASS_HE
branch research/he32-sandbox-primordial-pilot-20261021
PR https://github.com/cosmosapjw-quantum/BASS_HE/pull/85
unit research/he32_sandbox_primordial_20261021
science evidence pin 8d32c9944acffbeed5dc98325d283bf0c3b506f0
복원에 사용한 final docs pin 88f9957d219f71b458b3bcaf41ccdde60538379f
최신 additive 복원 기록: evidence/recovery/resume_20261022/RESUME_RESTORED_20261022.json

392 nominal + 2 L24 guard, 평균 z20→2, 21 populations, 그림6쌍 완료.
2026-10-22 파일 복원도 완료했으며 이번 새 IVP는0이다.
먼저 README, RESULTS_KO, DAG, 위 복원 기록을 읽는다.
Git에는 raw NPZ/PNG가 없으므로 검증된 전체 archive로 results만 별도 복원한다.
archive SHA256 27cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a
Dropbox ID id:BSpOijBcT10AAAAAAD_hsw
현재 sandbox results: /tmp/he32_resume_20261022/restored/research/he32_sandbox_primordial_20261021/results
plot --out은 REUSED_COMPLETE_RENDER를 반환했다.
완료된 identity를 새 경로/라벨로 재적분하지 않는다.
rei_bianchi로 전달할 때 NPZ/receipt/source identity와 signed stress 규약을 유지한다.
새 pending 작업이 실제로 생긴 경우에만 기존 cooperative runner로 NCP의
실제 CPU/RAM 여유와 shared leases 안에서 worker를 배정한다.
다른 job을 중지하지 않고 worker당 native thread1개를 유지한다.
```

## 다음 ChatGPT 스레드 handoff — 복사 가능

```text
$physmath-research-loop로 HE32 완료 상태에서 이어가라.
workflow1.0.0 / approval0.2의 현재 단원을 유지한다.
repo/branch/PR/unit과 archive identity는 바로 위 Codex handoff와 같다.
evidence/recovery/resume_20261022/RESUME_RESTORED_20261022.json을 먼저 읽어라.
2026-10-22에는 유실된 실행공간을 Git + 검증된 전체 archive로 복원했고
394 NPZ,394 receipts,그림6쌍,30stagearchive를 확인했다.
plot 재사용 확인은 exit0, 새 IVP/render/benchmark0이다.
기존 연구 DAG는30/30이며 변경하지 않았다.

이번에는 기존 완성본의 파일 복원만 했으므로 다른 repo/대화의 전수 재조사를
했다고 쓰지 말라. 선행 문헌/율/provider/검토는 기존 evidence를 재사용한다.
새 과학 단원이 필요하면 원래 목표와 남은 물리 범위의 차이를 명시하고,
바리온 비등방응력, 열·광원 진화, CI/DR/CX 또는 추가 종 범위의 의존성을
선택해 별도 DAG로 시작하라. 현재 모델은 8핵종21상태의 prescribed UV
photo+caseA RR pilot이고, 모든 isotope/ion/분자 또는 fully reactive
19채널 핵반응망의 완료를 뜻하지 않는다.
각 단계 백업/게시/진척/다음DAG를 명시하고 이미 완료된 IVP는 반복하지 말라.
```
