# RUN13 / RUN14 환경 소실 후 복구 완료 기록

기록 범위: `/root/repo_inventory`가 환경 소실 이후 새로 실행한 원본 복원·바이트 비교·저장 endpoint 재구성. source identity는 `cosmosapjw-quantum/rei_bianchi`의 실제 Git commit `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`이다.

## 현재 확립한 항목

1. 원래 Git transport helper로 두 nested ZIP을 실제 복원했다. 원본 manifest 332개 항목과 이를 포함한 정확히 333개 payload 파일이 일치한다. source/input 113개 항목(91 code, 19 inputs, 3 core Python)도 모두 일치한다. 원래 RUN13 범위의 tracked 파일 342개를 Git blob/mode와 전후 대조했고 Git index 실제 바이트가 변하지 않았다. 이 tracked342 숫자는 새 RUN15 case의 유실 파일342와 다른 집합이다.
2. 독립적으로 다시 다운로드한 41,075,268-byte RUN13 ZIP의 SHA-256 `6912c7f90dedaaee312d3fdc3248e4e8839409c0fb2944262de945e1b2f34e96`를 검산하고, ZIP 모든333 member의 실제 바이트를 Git-restored 파일과 직접 대조했다. 모두 일치했다. 모든 entry를 읽어 CRC도 확인했고 duplicate/traversal/link/encryption 여부를 검사했다.
3. 원래 m1/m2 standard/tight 네 저장 endpoint에서 원래 physical-owner 코드의 21개 관측량씩 총84개를 재구성했다. **84/84 exact float equality**다. 원래 코드·packet·geometry·state 파일24개를 별도 디렉터리에 hash 일치 복사하고, sealed-parent 또는 COMPLETE protocol reader와 원래 SpectralModel.observables만 호출했다. 원래333 디렉터리와 선택 source/input 바이트는 그대로다. Native binary는 SHA identity만 기록했고 실행하지 않았다.
4. Dropbox에서 RUN14 UNIT01/02 analysis JSON 원본 바이트를 실제 HTTP200으로 다시 받았다. 각각31,566/37,338 bytes이고 원래 SHA `153e32334bf1051c9e2a596565d4a2da23b6ef27a66aee87b1e462f4b1609a00` / `f7d053d73de5190571aa8e520be08e616ab28ad0b31f66e134f9d1f3b463ed43`와 일치한다. Dropbox content hash도 둘 다 일치한다. 이 파일들은 분석 JSON 원본이고, 별도 native trajectory state 전체 복원을 뜻하지 않는다.
5. 원래45-node DAG는 RUN13→RUN09→RUN08→RUN07→RUN06→RUN05 nested archive의 `ssot_v1/DAG.json`에서 원문 바이트 그대로 추출했다. 원래26-node DAG는 Git blob `1383fbb77ffff8a81c5dd4f1353beaa7d7efd522`에서 읽었다. 두 원문은 이전 source snapshot에 기록한 SHA와 일치하며 어떤 노드도 재정의·축소하지 않았다.

## 저장 endpoint가 재확인한 수치와 범위

| case | dimension | event intervals | exact matched observables | first-cell sub-H-fit survivor (comoving m^-3) |
|---|---:|---:|---:|---:|
| m1 standard |35,237|3,200|21|3.963580101474543e-12|
| m1 tight |35,237|3,200|21|3.963580101474519e-12|
| m2 standard |40,357|6,241|21|8.255385244169650e-12|
| m2 tight |40,357|6,241|21|8.255385244169626e-12|

standard m2를 분모로 한 작은 sub-H 성분 차이는 **0.5198794502929087**이다. 동일하게 저장된 상태에서 재확인한 값이며, 이 복원 단위가 만든 새 IVP 결과가 아니다. 전체 survivor의 작은 차이를 이 성분의 수렴으로 승격하지 않는다.

저장 state에서 독립 fsum 집계를 하고, m2 tight−standard 및 tight/standard m2−m1 세 대조에서 ΔP+ΣΔA−ΔB와 ΔR을 계산했다. 세 항등식의 fsum 차이는 모두0.0이고, float primaries를 정확히 변환한 Decimal100 연산에서도 결함은0이다. 이는 signed ledger의 대수적 일관성 확인이며, spectral error bound나 ODE tolerance 인증이 아니다.

## Evidence 경로

- Git 복원: `attempt02/POST_LOSS_RUN13_GIT_ONLY_RESTORATION.json` (SHA `09f3312acac79a5194fe83f3bb9d080958d1a911f32c6524423e2972b746cf5e`).
- ZIP/Git 원본333 cross-source 비교: `POST_LOSS_RUN13_CROSS_SOURCE_333.json` (SHA `44f06b35a77a0437da6294b2d2c96b6b627274d68fb5bc7f25e0ce23764699f8`).
- 저장 endpoint84 재구성: `postloss_endpoint_reconstruction/POST_LOSS_SAVED_ENDPOINT_84_RECEIPT.json` (SHA `0924578d70cb1eaf2d4f30315f4a974c14ea95094f3a100f0d341eb8879fb86e`).
- 정확한 실행 argv/cwd/environment/exit code 및 stdout/stderr: `POSTLOSS_ENDPOINT_EXEC.command.json`과 동명 logs. 환경은 Python3.12.14, NumPy2.3.5, SciPy1.17.0, BLAS/OMP/MKL threads1, Python -B다.
- RUN14 raw JSON 및 실제 download receipt: `run14/`. 민감한 단회용 다운로드 URL을 durable receipt에 넣지 않았다.
- 원래 DAG45/26 및 extraction provenance: `dag/`. 원래 DAG45 SHA `98c592052801ba34e02658d0906ad7e703dff32dd66d8072d19988f039a02543`, DAG26 SHA `c6459b3987aeac80e619ec435dbf89a069b1b6e2eac7059748f7e9dc94b8d1b9`.

## 보존한 실패와 남은 한계

첫 실행의 전체 `git status`는 sparse/promisor checkout의 외부 object를 추가 fetch하려다 sandbox의 `browser-proxy:8889` 연결 실패로 끝났다. 실패 로그를 보존하고, 두 번째 새 검증에서는 확보된 RUN13 범위의 Git blob/mode 및 Git index 바이트 검사를 사용했다. 전체 역사적 Git checkout과 모든 toolchain을 독립 복원했다는 주장은 하지 않는다.

이 agent는 원래 새 RUN15 case archive의342 파일 바이트를 현재 surface에서 회수하지 못했다. 기대 hash와 이전 검증 대화 재기록은 `../archive/TRANSCRIPT_ARCHIVE_RECOVERY_20261019.json`에서 **TRANSCRIPT_RECONSTRUCTION_ONLY**로 분리했다. 원래 소스나 state를 숫자·hash로 추측 재구성하지 않았다. 반면 retained literal tool output에서 회수한 `verify_clean_git_restore.py`와 `restore_inputs.py`, 새 Git에서 회수한 원래 transport helper는 원래 SHA와 일치해 **EXACT_BYTES_RECOVERED**로 별도 admission했다.

이 완료 기록에 해당하는 새 IVP, native process, 기존 test suite 실행은 각각0회다. 이후 parent 또는 다른 agent가 수행하는 별도 bounded 진단과 혼합하여 count하지 않는다.
