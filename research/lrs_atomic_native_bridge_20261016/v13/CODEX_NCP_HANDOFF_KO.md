# Codex 실행 전용: REI-LRS V13

Repo cosmosapjw-quantum/rei_bianchi, branch research/rei-lrs-v13-sourceon-average-photons-20261018. 실행 소스 anchor b73ebba15ca523bfcf67f7d16d7b1c9fd1859769, parent PR195 46b567e0ee96e725a21e77fed9ab4160d0ffa9e7. 최신 branch HEAD를 fetch하고 이 anchor의 후손인지 확인한다. AGENTS.md, v13/README_KO.md, stages/C8_RESULTS.md, SOURCE_DELTA.json과 RUN_V13.sh를 읽는다.

사용자에게 파일 다운로드·수동 SSH·전송을 요구하지 않는다. 새 solver를 설계/구현하는 임무가 아니다. 네 Rust 파일 변경, 테스트, 분석기와 실행기는 이미 sandbox에서 실제 컴파일·실행됐다. 기존 인증으로 GitHub에서 v13과 sibling v12/native_owner를 Codex가 직접 확보한다. 원본 checkout의 dirty 파일과 production PR150·PR195·NCP checkpoint는 보존한다.

NCP 접속은 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`. hostname/time/CPU/RAM/disk/load와 활성 작업을 먼저 확인한다. 키나 토큰은 로그에 기록하지 않는다. 기존 프로세스를 종료하지 않고 `/root/REI_LRS_V13_<UTC>/input/{v12/native_owner,v13}`에 자료를 자동 전송한다. NCP의 기존 Rust를 사용하고 필요시 /root/.cargo/bin을 PATH에 추가한다.

다음 완성된 명령을 실제 새 경로로 치환해 NCP에서 실행한다:

```bash
export V13_BASE=/root/REI_LRS_V13_<UTC>/input/v12/native_owner
export V13_RUN_ROOT=/root/REI_LRS_V13_<UTC>/run
export CARGO_BUILD_JOBS=2
export V13_MAX_N=256
export V13_CELLS=32
export V13_NONLINEAR_TOL=1e-15
bash /root/REI_LRS_V13_<UTC>/input/v13/RUN_V13.sh
```

RESTORE_NATIVE.py는 원본 사본에 압축 patch를 자동 적용하고 실제 테스트한 네 결과파일 SHA를 검사한다. RUN_V13.sh는 offline/locked release 빌드,29표적테스트,7제어군×6시간분할×두구간=84이력7056단계, CSV분석과 EXECUTION_RECEIPT.json을 생성한다. 먼저 smoke가 필요한 경우 새 폴더에서 V13_MAX_N=16,V13_CELLS=8을 사용한다. 본 실행 후 필요한 분해능만512/1024로 별도 새 경로에 추가한다. Existing output overwrite 및 experimental checkpoint resume는 금지다.

허용되는 작은 수정은 PATH/파일경로/동일 identity의 누락 입력 복구뿐이다. 모델·rate·source·spectral closure·수치허용치 변경은 이번 실행계약 밖이다. 변경이 필요하면 해당 경로를 HOLD하고 로그·부분 결과를 보존한다. 빌드job은1–4, 원래 실행timeout240/180초를 변경할 때 자원사유를 기록한다.

현재29표적테스트는 통과했으나 broad crate334PASS/16FAIL은 V12 source capsule에 없는 BASS/signed continuation fixture 때문에 발생했다. 이를 숨기거나 전체회귀PASS로 표시하지 않는다. 기존119개 sandbox이력과 새 NCP실행은 따로 센다.

가스/광자 양수성, source-birth/absorbed/survivor 및 species photo events/binding/heat, CE/RRDR/FF/CMB와 geometric work를 검사한다. CSV에 없는 전체 CI/RR event계수의 전수 보존 통계를 만들어내지 않는다. signed self-difference와 해상도별값을 보고하며 부호상쇄나 작은 차수만으로 source-on2차를 선언하지 않는다. common midpoint source halves는 retarded GL2 source-age가 아니다. source-on 독립연속RHS,fullEoR,CaseB,signedBianchi,uniformstiff는 HOLD 유지다.

원시 결과와 테스트/실행명령/소스SHA/출력SHA/host/time/resource를 로컬로 회수해 독립 branch에 commit/push하고 Draft PR에 보고한다. production merge 금지. Google Drive REI_RESEARCH_BACKUPS/rei_bianchi/REI_LRS_V13_SOURCEON_AVERAGE_20261018/ 및 Dropbox bianchi/research_backups/rei_bianchi/ 에 새 결과를 create-only 백업하고 양쪽 실제 원격 readback SHA를 검증한다. 한쪽 실패를 이중백업 완료로 표시하지 않는다.

최종 한국어 보고는 실제 NCP compile/test/history 수, 관측량별 signed수렴, 에너지/광자회계, 오류와작은수정, source-onHOLD, GitHub 및 두백업SHA를 포함한다. 목적은 이미 완성된 코드를 실행·재현하는 것이며 사용자 추가처리 없이 진행한다.
