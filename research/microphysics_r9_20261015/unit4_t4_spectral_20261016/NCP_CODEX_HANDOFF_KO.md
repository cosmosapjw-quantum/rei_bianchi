# R9 Unit4 — 저장된 daughter 보완상태의 에너지 분포 계산

현재 작업은 회수에 성공한 Unit3의 다음 T4 계산이다. 기존 바닥상태 FCI를 반복하지 말고, 아래의 완성된 실행기를 NCP에서 실행하고 결과를 회수·검토·백업·게시하라. 사용자는 이 연구의 NCP 실행과 기존 GitHub/Drive/Dropbox 목적지 게시를 승인했다.

## 시작 위치와 읽을 자료

기존 로컬 checkout `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi`의 현재 AGENTS.md, branch/HEAD/dirty/untracked 상태를 먼저 확인한다. 별도 clone/worktree를 만들거나 현재 branch를 바꾸지 말고 관련 없는 변경을 보존한다. 이 인계의 연구 기준은 PR151 commit `284916e758d87852a6137fbbb36befe83f15d271`의 Unit3 회수이며, 새 Unit4 게시 commit은 이 패키지의 외부 DELIVERY receipt에서 확인한다. 실제 실행 시 최신 PR151 head도 읽어라.

전체 패키지는 `REI_R9_UNIT4_T4_SPECTRAL_20261016.tar.gz`이다. 기존 SSH 설정으로 NCP의 새 staging 디렉터리에 옮겨 풀어라. 기존 `/root/REI_MICROPHYSICS_R9_20261015`를 덮어쓰지 않는다. 인증정보를 추측하거나 출력하지 않는다.

먼저 `spec/NEXT_T4_CONTRACT.md`, `spec/NEXT_T4_DERIVATION.md`, `review/INDEPENDENT_REVIEW.md`, 실행기 안내와 `results/`의 실제 로컬 검증 기록을 읽어라. 입력은 `inputs/receipt.json`, `inputs/data.npz`이며, 원래 V6 source는 `baseline/microphysics_driver_v6.py`이다. 원시 파일의 identity는 계약에 고정되어 있다.

## 이미 끝난 계산과 이번 계산

Li→Be+ aug-TZ 기존 계산은 정상 종료했다. P_ground=0.5756391820077925, unresolved complement=0.42436081799220793, retained orbitals=92이며 회수와 86개 수치 기준은 검토되었다. 새 실행은 저장된 X와 실제 expanded AO shells에서 동일 Be+ Hamiltonian을 재구성한다. SCF/FCI 바닥상태 또는 새 orbital eigensolve를 수행하지 않는다.

대상은 Q=I−|g><g|, K=Q(H−E0)Q와 q=Q|i>로 정의되는 **유한공간 보완상태 스펙트럼**이다. 공개된 연속상태 단면적이나 exclusive ionization probability로 해석하지 말라. Scalar 모멘트는 이미 여기서 계산했지만, NCP Hamiltonian 재구성과 실제 92-orbital Lanczos 실행은 아직 수행되지 않았다.

## 실제 NCP 실행

먼저 기존 Unit4 실행 또는 완료 결과가 있는지 확인하여 중복 제출을 피한다. 실제 CPU/RAM과 다른 owner 작업을 확인한다. PR150 transport/postprocessor는 별도 작업이며 이 인계로 변경하거나 중단하지 않는다. 12 threads/24 GiB/7200 s와 실행 중 20 GiB host headroom은 상한·정지 기준이고 예약된 자원이 아니다.

예를 들어 `/root/REI_R9_UNIT4_T4_SPECTRAL_20261016`에 패키지를 풀었다면:

```bash
cd /root/REI_R9_UNIT4_T4_SPECTRAL_20261016
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="/root/REI_R9_T4_SPECTRAL_${stamp}"
/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python \
  code/t4_spectral.py run \
  --receipt inputs/receipt.json --data inputs/data.npz \
  --v6-source baseline/microphysics_driver_v6.py \
  --contract spec/NEXT_T4_CONTRACT.json \
  --out "$out" --threads 12 --memory-gib 24 --wall-s 7200
```

`--help`와 실행기 안내를 함께 확인하라. 기존 NCP 환경을 사용하고 설치된 PySCF/NumPy/SciPy를 임의로 업그레이드하지 않는다. CLI의 supervisor가 자기 worker의 wall/RSS 및 host headroom을 감독하도록 한다. CLI exit 0만으로 과학적 성공을 판정하지 않는다.

재구성 기준을 통과하면 한 Lanczos basis를 16→32→64로 연장한다. 선언한 broadening별 refinement가 64에서 부족하고 동일 예산이 남아 있을 때만 128로 연장한다. 실행기가 남긴 checkpoint·milestone·stdout/stderr·자원 측정·receipt를 보존한다. 구현되지 않은 resume 인터페이스를 가정하지 않는다.

## 결과 해석과 반환

재구성 실패는 saved X/AO ordering/source/runtime와 실제 측정값으로 진단한다. 허용 오차를 넓히거나 기존 FCI를 자동 반복하지 않는다. 코드 변경이 필요하면 기존 실패를 보존하고 좁은 수정과 해당 회귀 검증을 수행한다.

완료 시 actual H-action 수, 재구성 잔차, Gram/ground leakage, 직접 첫 두 에너지 모멘트와 quadrature 일치, 실제 노드/가중치, broadening별 32→64 또는 64→128 차이, window 밖 확률, Ritz residuals를 보고한다. Refinement 미달은 보존할 유한 계산 결과이며 physical no-go가 아니다. PySCF adapter 검증, 유한공간 수렴, 완전기저/연속상태 물리 closure를 구분하라.

원시 결과를 새 immutable 결과 archive로 묶고 기존 rclone `dbx`, `gdrv` 설정을 사용하여 `/BASS_DERIVATION_DOSSIERS_20260912/`와 Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`에 이중백업한다. 성공 object ID·크기·checksum을 기록한다. 다른 게시 작업의 완료를 원시 결과 회수의 선행조건으로 만들지 않는다.

PR151의 현재 head를 확인하고 `research/microphysics_r9_20261015/unit4_t4_spectral_20261016/`에 task-owned compact receipt·수정 source·검토·backup 링크만 fast-forward로 추가하라. 큰 NPZ/checkpoint는 백업으로 연결한다. Force push, merge, production activation은 하지 않는다. 최종 답변에는 실제 수행 결과와 남은 정확한 물리 의존성을 반환하라.
